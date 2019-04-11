
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
        self._sensors['vision'] = api.sensor.vision("Vision_sensor")

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
        if len(vision_result) > 1:
            blob_data = vision_result[1]
            position = ''
            blob_size = 0
            blob_count = int(blob_data[0])
            if blob_count>0:
                print('blobs: ', blob_count)
                blob_size = blob_data[2]
                if blob_size >= 0.65:
                    return "close", round(blob_size, 5)
                if 0.35 < blob_data[4] < 0.65:
                    return "center", round(blob_size, 5)
                if 0.0 < blob_data[4] < 0.35:
                    return "left", round(blob_size, 5)
                if 0.65 < blob_data[4] < 1:
                    return "right", round(blob_size, 5)
            return position, round(blob_size, 5)
        else:
            return '', 0

    def vision(self):
        resolution = [32, 32]
        # raw_image = self._sensors['vision'].raw_image()
        code, state, vision_result = self._sensors['vision'].read()
        position, size = self.get_vision(vision_result)
        out = (position, size)
        print('vision:', out)
        return out

    def get_percepts(self):
        out = {'left': self.left_distance(),
               'center': self.center_distance(),
               'right': self.right_distance(),
               'vision': self.vision()
               }
        # out = {'left': self.left_distance(), 'center': self.center_distance(), 'right': self.right_distance()}
        return out

    def process_commands(self, commands):
        print(commands)
        for cmd in commands:
            self.invoke(cmd['cmd'], cmd['args'])

    def invoke(self, cmd, args):
        print('invoke', cmd, args)
        if cmd!= 'illegal_command':
            try:
                getattr(self.__class__, cmd)(self, *args)
            except AttributeError:
                raise NotImplementedError("Class `{}` does not implement `{}`".format(self.__class__.__name__, cmd))
