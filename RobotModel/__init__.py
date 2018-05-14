
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
        self._sensors['left'] = api.sensor.proximity(name+"_ultrasonicSensor3")
        self._sensors['right'] = api.sensor.proximity(name+"_ultrasonicSensor6")

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
        self._actuators['left'].set_target_velocity(left)
        self._actuators['right'].set_target_velocity(right)

    def right_length(self):
        return self._sensors['right'].read()[1].distance()

    def left_length(self):
        return self._sensors['left'].read()[1].distance()

