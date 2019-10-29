# pedro_v-rep_bridge
Protocol bridge between PEDRO messaging system for robotics and V-REP Remote API

Python robot controller that gets sensor data from V-REP simulator sending percepts to a PEDRO/QuProlog/Teleor program and receving motion commands (actions) from it. Here we user the PioneerP3DX V-REP mobile robot model, but you can easily replace it with the model you prefer just changing the names and the arrangement of the sensors and actuators.

## Requirements

V-REP robot simulator, PEDRO server and QuLog/Teleor clients are needed:
-  http://www.coppeliarobotics.com/
-  http://github.com/AAAI-DISIM-UnivAQ/vrep-api-python
-  http://staff.itee.uq.edu.au/pjr/HomePages/PedroHome.html
-  http://staff.itee.uq.edu.au/pjr/HomePages/QulogHome.html
-  http://redis.io  (optional)

## Nodes

Configuration for redis_control:

    V_REP robot --> robot_interface (Python3) --> REDIS --> your AI
    V_REP robot <-- robot_interface (Python3) <-- REDIS <-- your AI


Configuration for redis_control (+pedro):

    V_REP robot --> robot_interface (Python3) --> REDIS --> pedro_percepts -> PEDRO --> QuLog AI
    V_REP robot <-- robot_interface (Python3) <-- REDIS <-- pedro_actions <-- PEDRO <-- QuLog AI

Configuration for pedro_control:

    V_REP robot --> robot_interface (Python3) --> PEDRO --> QuLog AI
    V_REP robot <-- robot_interface (Python3) <-- PEDRO <-- QuLog AI

Like any V-REP project, you have to put the following files in the working directory, in order to run it:
-  vrep.py
-  vrepConst.py
-  the appropriate remote API library: "remoteApi.dll" (Windows), "remoteApi.dylib" (Mac) or "remoteApi.so" (Linux)
-  simpleTest.py (or any other example file) to test remote API functionality

Check the [vrep-api-python](https://github.com/Troxid/vrep-api-python) for details

## Robot control protocol

In the _redis_control_ configuration, the robot is controlled by the __ROBOT__ redis channel,  while it sends its sensor readings to the __ROBOT:PERCEPTS__ redis channel.

### Protocol

__Percepts__:

    sonar( Ld, Cd, Rd)
    Ld Left distance
    Cd Center distance
    Rd Right distance

of type floating point, meters from obstacles. Became very large to represent nothing (+ infinity)

    vision ( Position, Width, Base, Height ) red bottle detection
    Position: close|center|left|right
    Width, Base, Height : floats  
    
__Actions__:

    turn_right(speed)
    turn_left(speed)
    move_forward(speed)

of type floating point, meters per seconds.
