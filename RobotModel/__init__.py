import math

from pyvrep import VRep
from WorldModel import WorldModel
import json
import time

class RobotModel:
    def __init__(self, name: str, api: VRep):
        self._api = api
        self._name = name
        self._sensors = None    # some kind of collection class
        self._actuators = None  # idem
        self._world = WorldModel()

class PioneerP3DX(RobotModel):

    def __init__(self, name: str, api: VRep):
        RobotModel.__init__(self, name, api)
        self._actuators = {}
        self._sensors = {}
        # self._signals = {}
        self._actuators['left'] = api.joint.with_velocity_control(name+"_leftMotor")
        self._actuators['right'] = api.joint.with_velocity_control(name+"_rightMotor")
        self._sensors['left'] = api.sensor.proximity(name+"_ultrasonicSensor3")
        self._sensors['center'] = (api.sensor.proximity(name+"_ultrasonicSensor4"), api.sensor.proximity(name+"_ultrasonicSensor5"))
        self._sensors['right'] = api.sensor.proximity(name+"_ultrasonicSensor6")
        self._sensors['vision'] = api.sensor.vision("Vision_sensor")
        self._sensors['compass'] = api.sensor.position("Pioneer_p3dx")
        self._set_two_motor(0.0, 0.0)
        self._last_commands = None

    def turn_right(self, speed=2.0):
        print('turn_right', speed)
        self._set_two_motor(speed, -speed)

    def turn_left(self, speed=2.0):
        print('turn_left', speed)
        self._set_two_motor(-speed, speed)

    def move_forward(self, speed=2.0):
        print('move_forward', speed)
        self._set_two_motor(speed, speed)

    def move_backward(self, speed=2.0):
        self._set_two_motor(-speed, -speed)

    def _set_two_motor(self, left: float, right: float):
        self._actuators['left'].set_target_velocity(left)
        self._actuators['right'].set_target_velocity(right)

    def right_distance(self):
        for _ in range(5):
            # try to read sensor up to 5 times
            a  = self._sensors['right'].read()
            coord = a[1]
            dis = coord.distance()
            if dis > 0.01:
                break
            time.sleep(0.005)

        # take the distance when the read state is true(it is true only if sensor detects some objects)
        if a[0]:
            coord = a[1]
            dis = coord.distance()
        else:
            dis = 1
            coord = None
        if dis > 9999: dis = 9999
        return dis, coord

    def left_distance(self):
        for _ in range(5):
            # try to read sensor up to 5 times
            a = self._sensors['left'].read()
            coord = a[1]
            dis = coord.distance()
            if dis > 0.01:
                break
            time.sleep(0.005)

        # take the distance when the read state is true(it is true only if sensor detects some objects)
        if a[0]:
            coord = a[1]
            dis = coord.distance()
        else:
            dis = 1
            coord = None
        if dis > 9999: dis = 9999
        return dis, coord

    def center_left_distance(self):
        for _ in range(5):
            # try to read sensor up to 5 times
            a = self._sensors['center'][0].read()
            coord = a[1]
            dis = coord.distance()
            if dis > 0.01:
                break
            time.sleep(0.005)
            # take the distance when the read state is true(it is true only if sensor detects some objects)
            if a[0]:
                coord = a[1]
                dis = coord.distance()
            else:
                dis = 1
                coord = None
        if dis > 9999: dis = 9999
        return dis, coord

    def center_right_distance(self):
        for _ in range(5):
            # try to read sensor up to 5 times
            a = self._sensors['center'][1].read()
            coord = a[1]
            dis = coord.distance()
            if dis > 0.01:
                break
            time.sleep(0.005)
        # take the distance when the read state is true(it is true only if sensor detects some objects)
        if a[0]:
            coord = a[1]
            dis = coord.distance()
        else:
            dis = 1
            coord = None
        if dis > 9999: dis = 9999
        return dis, coord

    def display(self, code):
        # res = self._api.simxCallScriptFunction(0, 'debug', self._api.sim_scripttype_mainscript,
        #                                          'show_debug', code, self._api.simx_opmode_blocking)
        print(f'display:{code}')

    def get_vision(self, vision_result):
        """
        extract blob data from vision sensor image buffer
            only sees red blobs

        blob_data[0]=blob count
        blob_data[1]=n=value count per blob
        blob_data[2]=blob 1 size
        blob_data[3]=blob 1 orientation
        blob_data[4]=blob 1 position x
        blob_data[5]=blob 1 position y
        blob_data[6]=blob 1 width
        blob_data[7]=blob 1 height
        ...
        :return: POSITION, SIZE
            POSITION: close, center, left, right
            SIZE: 0.0 .. 1.0
        """
        SIZE_THR = 0.3

        if len(vision_result) > 1:
            blob_data = vision_result[1]
            position = ''
            blob_size = 0
            blob_base = 0
            blob_height = 0
            blob_count = int(blob_data[0])
            if blob_count>0:
                # print('blobs: ', blob_count)
                blob_size = blob_data[6]  # red blob width
                blob_base = blob_data[5] - blob_data[7]/2.0 #yposition - half height =bottle y center coordinate
                blob_height = blob_data[7]
                print(f'blob_size:{blob_size}')
                if blob_size >= SIZE_THR:
                    return "close", round(blob_size, 5), round(blob_base, 3), round(blob_height, 3)
                if 0.0 <= blob_data[4] <= 0.25:
                    return "left", round(blob_size, 5), round(blob_base, 3), round(blob_height, 3)
                if 0.25 < blob_data[4] <= 0.5:
                    return "center_left", round(blob_size, 5), round(blob_base, 3), round(blob_height, 3)
                if 0.5 < blob_data[4] <= 0.75:
                    return "center_right", round(blob_size, 5), round(blob_base, 3), round(blob_height, 3)
                if 0.75 < blob_data[4] <= 1:
                    return "right", round(blob_size, 5), round(blob_base, 3), round(blob_height, 3)
            return position, round(blob_size, 5), round(blob_base, 3), round(blob_height, 3)
        else:
            return '', 0, 0, 0

    def vision(self):
        code, state, vision_result = self._sensors['vision'].read()
        print("Vision Result: ", vision_result)
        position, size, base, height = self.get_vision(vision_result)
        out = (position, size, base, height)
        return out

    def compass(self):
        orientation = self._sensors['compass'].get_orientation().get_gamma()
        print("Compass orientation: ", orientation)
        return orientation

    def get_percepts(self):
        out = {'left': self.left_distance(),
               'center_left': self.center_left_distance(),
               'center_right': self.center_right_distance(),
               'right': self.right_distance(),
               'vision': self.vision(),
               'compass': self.compass()
               }
        print(126, 'percepts:', out)
        self._world.robot_updates(self._last_commands, out)
        return out

    def get_signal(self, name):
        signalValue = 0
        return signalValue

    def process_commands(self, commands):
        t = time.process_time()
        self._last_commands = commands
        for cmd in commands:
            self.invoke(cmd['cmd'], cmd['args'])
        return  time.process_time() - t

    def invoke(self, cmd, args):
        # print('invoke', cmd, args)
        if cmd!= 'illegal_command':
            try:
                getattr(self.__class__, cmd)(self, *args)
            except AttributeError:
                raise NotImplementedError("Class `{}` does not implement `{}`".format(self.__class__.__name__, cmd))
