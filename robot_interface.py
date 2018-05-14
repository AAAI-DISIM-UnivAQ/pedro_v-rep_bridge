
# To run in Python3

'''
    Copyright @giodegas 2018
    Class to control a PioneerP3DX inside a V-REP robot simulator
        Percepts are sent to the ROBOT:PERCEPTS redis channel
        Actions are received through the ROBOT redis channel
'''

from RobotControl import demo_control, redis_control, pedro_control


## MAIN - Select your control function

if __name__ == '__main__':
    #demo_control()
    #redis_control()
    pedro_control()
