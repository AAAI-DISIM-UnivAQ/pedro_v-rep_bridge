
# To run in Python3

'''
    Copyright @giodegas 2018
    Class to control a PioneerP3DX inside a V-REP robot simulator
        Percepts are sent to the ROBOT:PERCEPTS redis channel
        Actions are received through the ROBOT redis channel
'''

import threading

from pyrep import VRep
import time
from math import tanh, log
from redis import Redis

class PioneerP3DX:

    def __init__(self, name: str, api: VRep):
        self._api = api
        self._name = name
        self._left_motor = api.joint.with_velocity_control(name+"_leftMotor")
        self._right_motor = api.joint.with_velocity_control(name+"_rightMotor")
        self._left_sensor = api.sensor.proximity(name+"_ultrasonicSensor3")
        self._right_sensor = api.sensor.proximity(name+"_ultrasonicSensor6")

    def rotate_right(self, speed=2.0):
        print('rotate_right', speed)
        self._set_two_motor(speed, -speed)

    def rotate_left(self, speed=2.0):
        print('rotate_left', speed)
        self._set_two_motor(-speed, speed)

    def move_forward(self, speed=2.0):
        print('move_forward', speed)
        self._set_two_motor(speed, speed)

    def move_backward(self, speed=2.0):
        self._set_two_motor(-speed, -speed)

    def _set_two_motor(self, left: float, right: float):
        self._left_motor.set_target_velocity(left)
        self._right_motor.set_target_velocity(right)

    def right_length(self):
        return self._right_sensor.read()[1].distance()

    def left_length(self):
        return self._left_sensor.read()[1].distance()

def demo_control():
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

## MAIN - Select your control function

# demo_control()

redis_control()
