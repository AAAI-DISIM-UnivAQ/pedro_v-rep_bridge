# Installation instructions

## General sequence in Windows

* Install PEDRO setup from PEDRO web site
* Install QuProlog setup from QuProlog web site
* Update your PATH environment to include pedro  and QuProlog/bin folder
* Install QuLog/Teleor binary installer taken from this moodle server
* Update your PATH environment to include qulog/bin folder

## Detailed sequence for Linux:

In order to run __pedro_v-rep-bridge__ project follow the next steps:

* Install Python 3.7, PyCharm Community and V-rep Pro Edu.
* Install Pedro server (http://staff.itee.uq.edu.au/pjr/HomePages/PedroHome.html)
  * Extract the _Pedro.tgz_ archive where you want;
  * In the extracted _QuProlog_ folder, open a new terminal window and run the following:
      
     ./configure
     make
     make install
     make clean
     
  * Test Pedro: `run 'pedro -L stdout'` command in the same terminal. It should start the pedro 
  server logging to the console
  
* Install [QuProlog](http://staff.itee.uq.edu.au/pjr/HomePages/QuPrologHome.html)
   * Extract the _QuProlog.tgz_ archive where you want;
   * In the extracted QuProlog folder, open a new terminal window and run the following:
   

    ./configure
    source PROFILE_CMDS   
    make
     
* Test QuProlog: running `qp` command in the same terminal. 
It should open QuProlog interpreter. In the interpreter type `X is 2*3.` if everything is working it should say `X = 6`.
  
    __NOTE__: make sure that qc file in bin folder is present otherwise an error will occur during QuLog installation (step 3). If qc file is not present delete the QuProlog folder and restart from step 2.1

* Install __QuLog__
   * Extract the QuLog tgz archive where you want;
   * In the extracted QuLog folder, open a terminal window and run the following:


     ./configure
     source PROFILE_CMDS
     source QUPROLOG_INSTALLATION_FOLDER/PROFILE_CMDS
     make
        
* Test Qulog: run `teleor` command in the same terminal. It should open teleor interpreter.
   
__NOTE__: if you want run Teleor or QuProlog from 
everywhere you should add the path of their bin 
folders in the `$PATH` environment variable.

* Open pedro_v-rep-bridge project in PyCharm
  * In Welcome to PyCharm wizard click on Check out from Version Control and select Git, paste the URL (https://github.com/AAAI-DISIM-UnivAQ/pedro_v-rep_bridge.git) and clone
  * Install requirements (consider to create a python 3 virtual environment)
  * Open V-Rep and load __scene.ttt__ present in `pedro_v-rep-bridge` folder
  * Run pedro server: `pedro -L stdout`

* Execute teleor teleo_ai file
  * In the qulog installation folder run `source PROFILE_CMDS` then move to `pedro_v-rep_bridge/AI` folder and run teleor interpreter: `teleor -Arobot`
  * In the teleor interpreter consult teleo_ai file ([teleo_ai].)
  * In the teleor interpreter to activate the logger type 'logging logging.'
  * In a new terminal run `logger.py logging` to read the log output
  * In the teleor interpreter type `go().`

* Run `robot_interface.py` in pycharm