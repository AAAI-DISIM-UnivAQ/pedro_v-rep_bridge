
from pyrep import VRep

class RobotModel:
    def __init__(self, name: str, api: VRep):
        self._api = api
        self._name = name
        self._sensors = None    # some kind of collection class
        self._actuators = None  # idem

class PioneerP3DX(RobotModel):

    def __init__(self, name: str, api: VRep):
        RobotModel.__init__(self, name, api)
        self._actuators = {}
        self._sensors = {}
        self._actuators['left'] = api.joint.with_velocity_control(name+"_leftMotor")
        self._actuators['right'] = api.joint.with_velocity_control(name+"_rightMotor")
        self._sensors['left'] = api.sensor.proximity(name+"_ultrasonicSensor2")
        self._sensors['center'] = (api.sensor.proximity(name+"_ultrasonicSensor4"), api.sensor.proximity(name+"_ultrasonicSensor5"))
        self._sensors['right'] = api.sensor.proximity(name+"_ultrasonicSensor7")

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
        dis = self._sensors['right'].read()[1].distance()
        if dis>9999: dis = 9999
        return dis

    def left_distance(self):
        dis = self._sensors['left'].read()[1].distance()
        if dis>9999: dis = 9999
        return dis

    def center_distance(self):
        dis = self._sensors['center'][0].read()[1].distance()
        dis += self._sensors['center'][1].read()[1].distance()
        dis /= 2
        if dis > 9999: dis = 9999
        return dis

    def get_percepts(self):
        return {'left':self.left_distance(), 'center':self.center_distance(), 'right':self.right_distance()}

    def process_commands(self, commands):
        for cmd in commands:
            self.invoke(cmd['cmd'], cmd['args'])

    def invoke(self, cmd, args):
        print('invoke', cmd, args)
        try:
            getattr(self.__class__, cmd)(self, *args)
        except AttributeError:
            raise NotImplementedError("Class `{}` does not implement `{}`".format(self.__class__.__name__, cmd))
