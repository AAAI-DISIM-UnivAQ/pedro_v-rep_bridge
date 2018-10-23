# How to start the QuLOG-PEDRO-Python-VREP simulation

Download this repo [http://github.com/AAAI-DISIM-UnivAQ/pedro_v-rep_bridge](http://github.com/AAAI-DISIM-UnivAQ/pedro_v-rep_bridge)

1. have VREP working

   use the "scene.ttt" virtual robotics scene file
	
2. start pedro message broker server with

    2.0 Install PEDRO-1.9
    
	2.1 copy pedroclient.py from the <pedro>/src/python_api
	in your project
	
`    pedro -L stdout
`
3. start the teleor/qulog controller

   from your project folder where you find the AI subfolder with
   the controller teleor program "robot_ai.qlg"

`   teleor -Acontroller `

`   [robot_ai].`

`   go(). `   


   
