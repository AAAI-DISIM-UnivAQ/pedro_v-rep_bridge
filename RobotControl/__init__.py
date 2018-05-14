
'''
    From here the Robot can be controlled by an AI, internal or external through a message system
    (Redis and/or PEDRO)
'''

from RobotModel import PioneerP3DX, VRep
import time
from math import tanh, log
from redis import Redis
from .pedro_controller import *

def demo_control():
    '''
        In process robot control. Just a simple navigation, avoiding to bump into anything.
    :return:
    '''

    with VRep.connect("127.0.0.1", 19999) as api:
        r = PioneerP3DX('Pioneer_p3dx', api)
        speed = 0.0
        while True:
            rl = r.right_length()
            ll = r.left_length()
            print('{0:.3f} {1:.3f} {2:.3f}'.format(speed, ll, rl))
            if rl > 0.01 and rl < 10:
                r.rotate_left()
            elif ll > 0.01 and ll < 10:
                r.rotate_right()
            else:
                speed = 10.0*tanh(log(ll)+log(rl))
                if speed>5.0:
                    speed = 5.0
                r.move_forward(speed=speed)
            time.sleep(0.1)

def invoke(obj, method_string):
    methL=  method_string.split('(')
    method_name = methL[0]
    args = float(methL[1])
    # method = getattr(obj.__class__, method_name)
    # print('invoking: ', method, args)
    try:
        getattr(obj.__class__, method_name)(obj, args)
    except AttributeError:
        raise NotImplementedError("Class `{}` does not implement `{}`".format(obj.__class__.__name__, method_name))

def redis_control():
    '''
            Percepts are sent to the ROBOT:PERCEPTS redis channel
            Actions are received through the ROBOT redis channel
    :return:
    '''

    with VRep.connect("127.0.0.1", 19999) as api:
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
                    invoke(r, cmd)
                except NotImplementedError:
                    print(cmd, 'not implemented!')
            # build percepts string
            rl = r.right_length()
            ll = r.left_length()
            percepts = '[sonar({0:.3f}, {1:0.3f})]'.format(ll, rl)
            if percepts!= prev:
                prev = percepts
                Red.publish('ROBOT:PERCEPTS', percepts)


def pedro_control():
    with VRep.connect("127.0.0.1", 19997) as api:
        myRobot = PioneerP3DX('Pioneer_p3dx', api)
        vrep_pedro = Vrep_Pedro(myRobot)
        # wait for and process initialize_ message
        vrep_pedro.process_initialize()

        previous_percept = None
        time.sleep(1)

        print('Connected to V-REP and PEDRO, listening...')

        while True:
            # build percepts string
            rl = myRobot.right_length()
            ll = myRobot.left_length()
            percept = '[sonar({0:.3f}, {1:0.3f})]'.format(ll, rl)
            if percept != previous_percept:
                previous_percept = percept
                vrep_pedro.send_percept(percept)
