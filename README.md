# pedro_c-sim_bridge
Protocol bridge between PEDRO messaging system for robotics and Coppelia Simulator Remote API

Python robot controller that gets sensor data from V-REP simulator sending percepts 
to a PEDRO/QuProlog/Teleor program and receving motion commands (actions) from it. 
Here we user the PioneerP3DX V-REP mobile robot model, but you can easily replace 
it with the model you prefer just changing the names and the arrangement of the sensors
 and actuators.

## Requirements

Coppelia Robotics robot simulator, PEDRO server and QuLog/Teleor clients are needed:
-  http://www.coppeliarobotics.com/
-  http://github.com/AAAI-DISIM-UnivAQ/vrep-api-python
-  http://staff.itee.uq.edu.au/pjr/HomePages/PedroHome.html
    - remember in Ubuntu:
        - autoreconf -f -i 
        - sudo apt-get install texinfo
-  http://staff.itee.uq.edu.au/pjr/HomePages/QulogHome.html 
   - (also install the required QuProlog compiler)
-  http://redis.io  (optional)

## Nodes

You can play with different configuration of hierarchical control:

Configuration for redis_control:

    C-SIM robot --> robot_interface (Python3) --> REDIS --> your AI
    C-SIM robot <-- robot_interface (Python3) <-- REDIS <-- your AI


Configuration for redis_control (+pedro):

    C-SIM robot --> robot_interface (Python3) --> REDIS --> pedro_percepts -> PEDRO --> QuLog AI
    C-SIM robot <-- robot_interface (Python3) <-- REDIS <-- pedro_actions <-- PEDRO <-- QuLog AI

Configuration for pedro_control:

    C-SIM robot --> robot_interface (Python3) --> PEDRO --> QuLog AI
    C-SIM robot <-- robot_interface (Python3) <-- PEDRO <-- QuLog AI

Like any C-SIM project, you have to put all the necessary file in a single working directory, 
to have to C-SIM Remote API working. 
Check the [csim-api-python](https://github.com/AAAI-DISIM-UnivAQ/csim-api-python) for details.

## Robot control protocol

In the _redis_control_ configuration, the robot is controlled by the __ROBOT__ redis channel,  
while it sends its sensor readings to the __ROBOT:PERCEPTS__ redis channel.

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
