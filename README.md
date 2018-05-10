# pedro_v-rep_bridge
Protocol bridge between PEDRO messaging system for robotics and V-REP Remote API

Python robot controller that gets sensor data from V-REP simulator asending percepts to a PEDRO/QuProlog/Teleor program and receving motion commands from it. Here we user the DR12 V-REP mobile robot model, but you can easily replace it with the model you prefer just changing the names and the arrangement of the sensors.


V-REP robot simulator, SWI-Prolog and PySWIP Python library are needed: 
-  http://www.coppeliarobotics.com/
-  http://staff.itee.uq.edu.au/pjr/HomePages/PedroHome.html


Like any V-REP project, you have to put the following files in the working directory, in order to run it:
-  vrep.py
-  vrepConst.py
-  the appropriate remote API library: "remoteApi.dll" (Windows), "remoteApi.dylib" (Mac) or "remoteApi.so" (Linux)
-  simpleTest.py (or any other example file) to test remote API functionality
