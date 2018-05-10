# coding : utf-8

'''
Licensed under the Apache License, Version 2.0 (the "License"); 
you may not use this file except in compliance with the License. 
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on 
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. 
See the License for the specific language governing permissions and limitations under the License
'''

import time
import os
import ctypes as ct
import platform
import vrepConst

try:
    import vrep
except:
    print ('--------------------------------------------------------------')
    print ('"vrep.py" could not be imported. This means very probably that')
    print ('either "vrep.py" or the remoteApi library could not be found.')
    print ('Make sure both are in the same folder as this file,')
    print ('or appropriately adjust the file "vrep.py"')
    print ('--------------------------------------------------------------')
    print ('')


class World(object):

    '''
    Robot simulator class to communicate with the simulation environment
    '''

    __host = None
    __portNumber = None
    __clientID = None

    def __init__(self, host='127.0.0.1', portNumber=19997):
        self.__host = host
        self.__port = portNumber
        self._rightWheel = None
        self._leftWheel = None

    def connect(self):
        '''
        Connect with V-REP Simulator.
        :return: True if the connection has been established, False otherwise.
        '''
        # just in case, close all opened connections
        vrep.simxFinish(-1)
        # Connect to V-REP
        self.__clientID = vrep.simxStart(self.__host, self.__port, True, True, 5000, 5)
        # check clientID for a good connection...
        if self.__clientID == -1:
            return False
        else:
            state, self._rightWheel = vrep.simxGetObjectHandle(self.__clientID, 'dr12_rightWheel_', vrep.simx_opmode_blocking)
            state, self._leftWheel = vrep.simxGetObjectHandle(self.__clientID, 'dr12_leftWheel_', vrep.simx_opmode_blocking)
            return True

    def act(self, command, dParams):
        '''
        Implements action commands in the robot world
        :param command: action command to execute
        :param dParams: action parameters
        :return: True is action was actuated
        '''
        assert isinstance(command, str)
        assert isinstance(dParams, dict)
        out = True
        if command == 'move':
            vrep.simxsetJointTargetVelocity(self._rightWheel, dParams['right'])
            vrep.simxsetJointTargetVelocity(self._leftWheel, dParams['left'])
        return out

    def sense(self, sensorName):
        '''
        Implements sensor reading from the robot simulator
        :param sensorName: name of the sensor as defined in the simulator
        :return: out:
            The 1st element of out is the state of the reading on the sensor (0 os ok).
            The 2nd element of out is a Boolean that says if the sensor is detecting something in front of it.
            The 3rd element of out is the point of the detected object.
            The 4th element of out is the handle of the detected object.
            The 5th element of out is the normal vector of the detected surface.
        '''
        assert isinstance(sensorName, str)
        state, handle = vrep.simxGetObjectHandle(self.__clientID, sensorName, vrep.simx_opmode_blocking)
        out = vrep.simxReadForceSensor(self.__clientID, handle, vrep.simx_opmode_blocking)
        return out

    def close(self):
        '''
        Close connection with the robot simulation
        :return:
        '''
        # Before closing the connection to V-REP, make sure that the last command sent out had time to arrive. You can guarantee this with (for example):
        vrep.simxGetPingTime(self.__clientID)
        # Now close the connection to V-REP:
        vrep.simxFinish(self.__clientID)

