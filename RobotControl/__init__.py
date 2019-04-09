
'''
    From here the Robot can be controlled by an AI, internal or external through a message system
    (Redis and/or PEDRO)
'''

from RobotModel import PioneerP3DX, VRep
import time
from math import tanh, log
from redis import Redis
import pedroclient
import queue
import threading

class Control(object):
    def __init__(self, host, port, sleep_time):
        self._host = host
        self._port = port
        self._sleep_time = sleep_time
        try:
            self._api = VRep.connect(self._host, self._port)
        except :
            print('V-REP not responding')
            exit(-1)

    def run(self):
        with self._api as api:
            r = self.make_robot(api)
            while True:
                r.process_commands(self.get_commands())
                self.process_percepts(r.get_percepts())
                time.sleep(self._sleep_time)

    def make_robot(self, api):
        return None

    def process_initialize(self):
        pass

    def process_percepts(self, percepts_method):
        pass

    def get_commands(self):
        pass

class DemoControl(Control):
    def __init__(self, host='127.0.0.1', port=19997, sleep_time=0.01):
        super().__init__(host, port, sleep_time)
        self._rl = 0 # right sensor reading
        self._ll = 0 # left
        self._cl = 0 # center

    def make_robot(self, api):
        return PioneerP3DX('Pioneer_p3dx', api)

    def process_percepts(self, percepts):
        self._ll = percepts['left']
        self._rl = percepts['right']
        self._cl = percepts['center']

    def get_commands(self):
        rl = self._rl
        ll = self._ll
        cl = self._cl
        if rl > 0.01 and rl < 10:
            return [{'cmd': 'turn_left', 'args': [0.5]}]
        elif ll > 0.01 and ll < 10:
            return [{'cmd': 'turn_right', 'args': [0.5]}]
        else:
            speed = 10.0
            if cl<10:
                speed = -1
            else:
                speed = 1
            if speed > 5.0:
                speed = 5.0
            return [{'cmd': 'move_forward', 'args': [speed]}]

# Handling messages from the TR program
class MessageThread(threading.Thread):
    def __init__(self, client, q):
        self.running = True
        self.client = client
        self.queue = q
        threading.Thread.__init__(self)
        self.daemon = True

    def run(self):
        while self.running:
            p2pmsg = self.client.get_term()[0]
            self.queue.put(p2pmsg)

    def stop(self):
        self.running = False

class PedroControl(Control):
    def __init__(self, host='127.0.0.1', port=19997, sleep_time=1.0):
        super().__init__(host, port, sleep_time)
        try:
            self.client = pedroclient.PedroClient()
        except ConnectionRefusedError as e:
            print('PEDRO server not responding', e)
            exit(-1)
        self.client.register("vrep_pedro")
        self.queue = queue.Queue(0)
        self.message_thread = MessageThread(self.client, self.queue)
        self.message_thread.start()
        p2pmsg = self.queue.get()
        self.percepts_addr = p2pmsg.args[1]

    def set_client(self, addr):
        self.percepts_addr = addr

    def send_percept(self, percepts_string):
        print("send_percept", str(self.percepts_addr), percepts_string)
        if self.client.p2p(self.percepts_addr, percepts_string) == 0:
            print("Error", percepts_string)

    def process_initialize(self):
        # Block unitil message arrives
        p2pmsg = self.queue.get()
        print(p2pmsg)
        message = p2pmsg.args[2]
        if str(message) == 'initialise_':
            # get the sender address
            percepts_addr = p2pmsg.args[1]
            print("percepts_addr", str(percepts_addr))
            self.set_client(percepts_addr)
            init_percepts = '[sonar(9999, 9999, 9999)]'
            self.send_percept(init_percepts)
        else:
            print("Didn't get initialise_ message")

    def make_robot(self, api):
        return PioneerP3DX('Pioneer_p3dx', api)

    def process_percepts(self, percepts):
        vision = percepts['vision']
        percept = '['
        percept += 'sonar({0:.3f}, {1:0.3f}, {2:0.3f})'.format(percepts['left'],
                                                               percepts['center'],
                                                               percepts['right'])
        if vision != ('','',0):
            # something has been seen
            vision_pred = f'vision( {vision[0]}, {vision[1]}, {vision[2]} )'
            percept += ', '
            percept += vision_pred
        percept += ']'

        self.send_percept(percept)

    def get_commands(self):
        cmds = []
        while not self.queue.empty():
            p2pmsg = self.queue.get()
            msg = p2pmsg.args[2]
            actions = msg
            for a in actions.toList():
                cmds.append(self.action_to_command(a))
        return cmds

    def action_to_command(self, a):
        cmd_type = a.functor.val
        cmd = a.args[0]
        if cmd_type == 'stop_':
            return {'cmd':'move_forward', 'args':[0.0]}
        else:
            if cmd.functor.val == 'move_forward':
                speed = cmd.args[0].val
                return {'cmd':'move_forward', 'args':[speed]}
            if cmd.functor.val == 'turn_left':
                speed = cmd.args[0].val
                return {'cmd':'turn_left', 'args':[speed]}
            if cmd.functor.val == 'turn_right':
                speed = cmd.args[0].val
                return {'cmd':'turn_left', 'args':[speed]}
        # maybe raise an exception?
        return {'cmd':'illegal_command', 'args':[str(a)]}

def redis_control():
    '''
            Percepts are sent to the ROBOT:PERCEPTS redis channel
            Actions are received through the ROBOT redis channel
    :return:
    '''

    with VRep.connect("127.0.0.1", 19997) as api:
        r = PioneerP3DX('Pioneer_p3dx', api)
        Red = Redis()
        pubsub = Red.pubsub()
        pubsub.subscribe('ROBOT')
        speed = 0.0
        print('listening..')
        prev = ''
        while True:
            msg = pubsub.get_message(ignore_subscribe_messages=True)
            if msg:
                cmd = msg['data'].decode('utf-8').split(',')[-1][:-1].strip()
                try:
                    r.invoke(cmd)
                except NotImplementedError:
                    print(cmd, 'not implemented!')
            # build percepts string
            rl = r.right_distance()
            ll = r.left_distance()
            percepts = '[sonar({0:.3f}, {1:0.3f})]'.format(ll, rl)
            if percepts!= prev:
                prev = percepts
                Red.publish('ROBOT:PERCEPTS', percepts)

def demo_control():
    '''
        In process robot control. Just a simple navigation, avoiding to bump into walls.
    :return:
    '''

    vrep_demo = DemoControl()
    vrep_demo.process_initialize()  # not needed in this case
    vrep_demo.run()


def pedro_control():
    '''
        Out of process robot control by a teleor AI
    :return:
    '''
    vrep_pedro = PedroControl()
    # wait for and process initialize_ message
    vrep_pedro.process_initialize()
    vrep_pedro.run()
