
'''
    Internal world model from the point of view of the robot
    Used for mapping and/or basic SLAM
'''

WORLD_SIZE = 100

import pygame

class WorldModel:

    def __init__(self):
        pygame.init()
        self._screen = pygame.display.set_mode((WORLD_SIZE, WORLD_SIZE))

    def digest_percept(self, percepts):
        '''
        :param percepts: new percepts from the robot from which it updates its
                internal world representation
        :return:
        '''
        pygame.display.update()
