# pedro_v-rep_bridge
Protocol bridge between PEDRO messaging system for robotics and V-REP Remote API

Python robot controller that gets sensor data from V-REP simulator sending percepts to a PEDRO/QuProlog/Teleor program and receving motion commands (actions) from it. Here we user the PioneerP3DX V-REP mobile robot model, but you can easily replace it with the model you prefer just changing the names and the arrangement of the sensors and actuators.

## Requirements

V-REP robot simulator, PEDRO server and REDIS server are needed: 
-  http://www.coppeliarobotics.com/
-  http://github.com/Troxid/vrep-api-python
-  http://staff.itee.uq.edu.au/pjr/HomePages/PedroHome.html
-  http://redis.io

## Nodes

    V_REP robot --> robot_interface (Python3) --> REDIS --> pedro_percepts -> PEDRO --> QuLog AI
    V_REP robot <-- robot_interface (Python3) <-- REDIS <-- pedro_actions <-- PEDRO <-- QuLog AI

Like any V-REP project, you have to put the following files in the working directory, in order to run it:
-  vrep.py
-  vrepConst.py
-  the appropriate remote API library: "remoteApi.dll" (Windows), "remoteApi.dylib" (Mac) or "remoteApi.so" (Linux)
-  simpleTest.py (or any other example file) to test remote API functionality

Check the [vrep-api-python](https://github.com/Troxid/vrep-api-python) for details

## Robot control protocol

The robot is controlled by the ROBOT redis channel and send its sensor readings to the ROBOT:PERCEPTS redis channel.

### Protocol

__Percepts__:

    sonar( Ld, Rd)

* Ld Left distance
* Rd Right distance

of type floating point, meters fro obstacles. Became very large to represent nothing (+ infinity)


__Actions__:

    rotate_right(speed)
    rotate_left(speed)
    move_forward(speed)
    move_backward(speed)

of type floating point, meters per seconds.
