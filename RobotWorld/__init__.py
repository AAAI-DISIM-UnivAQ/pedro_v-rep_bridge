# Partly provided by P. Robinson

# A template for connecting between teleor and VREP via Pedro

# For a given system we need:
# an agreed collection of percepts
# an agreed set of commands
# The idea is once the simulation is running in a loop
# we will be asking VREP for percepts in whatever form is best suited for
# VREP then translating (or possibly summarizing) these percepts into
# percept terms that teleo understands and sending them to the teleo agent
# via Pedro eg see(table, 10, 0)  (meaning seeing a table at 10 distance units
# dead ahead (0 degrees))
# The teleo agent will respond with commands - as in the example code below
# that are processed by the message thread


import pedroclient

import threading
import RobotWorld
import time

# Handling messages from the TR program
class MessageThread(threading.Thread):
    def __init__(self, parent):
        self.running = True
        self.parent = parent
        threading.Thread.__init__(self)
        self.daemon = True

    def run(self):
        while self.running:
            p2pmsg = self.parent.client.get_term()[0]
            # get the message
            message = p2pmsg.args[2]
            if str(message) == 'initialise_':
                # get the sender address
                percepts_addr = p2pmsg.args[1]
                self.parent.set_client(percepts_addr)
                # VREP code goes here so the visualization can
                # send back any initial percepts (iniital state)
                # create a string representing a list of initial percepts
                # say init_percepts and call
                # self.parent.send_percept(init_percepts)
                init_percepts = ''
                self.parent.send_percept(init_percepts)
                continue
            # As an example the teleor agent messages might be of the form
            # start_(move(lin_vel, ang_vel)) - starts a move
            # mod_(move(lin_vel, ang_vel)) - modify the velocities
            # stop_(move(lin_vel, ang_vel)) - stop moving
            if message.get_type() != pedroclient.PObject.structtype:
                continue
            functor = message.functor
            if functor.get_type() != pedroclient.PObject.atomtype:
                continue
            cmd_type = functor.val
            cmd = message.args[0]
            if cmd.get_type() != pedroclient.PObject.structtype:
                continue
            if cmd_type == 'stop_':
                if cmd.functor.val == 'move' and cmd.arity() == 2:
                    # translate the stop message as appropriate
                    # for VREP sending via self.vrep_client_id
                    pass
            elif cmd_type in ['start_', 'mod_']:
                if cmd.functor.val == 'move' and cmd.arity() == 2:     
                    linear_vel = cmd.args[0].val
                    angular_vel = cmd.args[1].val
                    # send new linear_vel, angular_vel to
                    # self.vrep_client_id
            
    def stop(self):
        self.running = False


class Vrep_Pedro(object):

    # sensors:
    # touching()
    #

    # motion:
    # move_forward(speed)
    # stop()
    # turnLeft(angleSpeed)
    # turnRight(angleSpeed)

    def __init__(self, vrep_client_id):
        self.vrep_client_id = vrep_client_id
        self.tr_client_addr = None
        self.client = pedroclient.PedroClient('127.0.0.1') #("192.168.0.153")
        # register vrep_pedro as the name of this process with Pedro
        self.client.register("vrep_pedro")
        self.message_thread = MessageThread(self)
        self.message_thread.start()
        self.set_client('127.0.0.1')

    # def methods for sensing and acting to the robot in the simulator
    def move_forward(self, speed):
        self.vrep_client_id.act('move', {'left':speed, 'right':speed})

    def stop_move(self):
        self.vrep_client_id.act('move', {'left':0, 'right':0})

    def turn_left(self, angleSpeed):
        self.vrep_client_id.act('move', {'left':angleSpeed, 'right':0})

    def turn_right(self, angleSpeed):
        self.vrep_client_id.act('move', {'left': 0, 'right': angleSpeed})

    def set_client(self, addr):
        self.tr_client_addr = addr

    def send_percept(self, percepts_string):
        if self.client.p2p(self.tr_client_addr, percepts_string) == 0:
            print("Error", percepts_string)

    def exit(self):
        self.message_thread.stop()
        self.client.p2p("messages:"+self.tr_client_addr,  "quiting")
        
# Initialize connection to VREP setting vrep_client_id 
# require VREP init code to go here

# this client_id is passed to the constructor below
vrep_client_id = RobotWorld.World(host='127.0.0.1', portNumber=19997)
vrep_pedro =  Vrep_Pedro(vrep_client_id)
vrep_client_id.connect()

while True:
    sensor = vrep_client_id.sense('dr12_bumper_')
    if sensor[1]>0:
        percept = '[touching()]'
    else:
        percept = '[free()]'
    vrep_pedro.send_percept(percept)
    time.sleep(1)

# e.g. clientID=vrep.simxStart('127.0.0.1',19999,True,True,5000,5)

# Here we need a VREP simulation loop
# I presume that in this loop we can step through the simulation
# and ask VREP for required percepts (in whatever form is easiest)
# and then convert to a percept string e.g.:
# "[see(table, 10, 0), touching(left)]"
# can be sent as
# vrep_pedro.send_percept("[see(table, 10, 0), touching(left)]")
# When we want to finish the simulation we want to call
# vrep_pedro.exit()
