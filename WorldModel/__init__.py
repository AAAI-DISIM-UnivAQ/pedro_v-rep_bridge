
from math import sin, cos, pi

'''
    Internal world model from the point of view of the robot
    Used for mapping and/or basic SLAM
'''

WORLD_SIZE = 500
REAL_SPACE_SPAN = 10 # meters
ORIGIN = [int(WORLD_SIZE/2), int(WORLD_SIZE/2)]
BLACK = (0, 0, 0)
RESOLUTION = REAL_SPACE_SPAN/WORLD_SIZE  # meters x pixel 0.1 mxp

import pygame

class WorldModel:

    def __init__(self):
        pygame.init()
        self._screen = pygame.display.set_mode((WORLD_SIZE, WORLD_SIZE))
        self._screen.fill(BLACK)
        self._sprite = pygame.image.load('graphics/cross8x8.png')
        self._rect = self._sprite.get_rect()
        self._position = [ORIGIN[0], ORIGIN[1]]
        self._translation = [0.0, 0.0]
        self._heading = pi/2 # south?
        self._rect = self._rect.move(tuple(self._position))
        self._last_cmd = ''
        self.screen_update()

    def move(self):
        self._position[0] += self._translation[0]
        self._position[1] += self._translation[1]
        delta = (int(self._position[0]-ORIGIN[0]),
                 int(self._position[1]-ORIGIN[1]))
        self._rect = self._rect.move(delta)
        print(38, self._position, delta, self._rect)

    def screen_update(self):
        self.move()
        self._screen.blit(self._sprite, self._rect)
        pygame.display.update()

    def robot_updates(self, commands, percepts):
        '''
        :param percepts: new percepts from the robot from which it updates its
                internal world representation
        :return:
        '''
        if len(commands)>0:
            cmd = commands[0]
            self._last_cmd = cmd
        else:
            cmd = self._last_cmd
        if cmd['cmd'] == 'move_forward':
            speed = cmd['args'][0] / RESOLUTION # in pixels x second
            self._translation = (speed * cos(self._heading),
                                 speed * sin(self._heading))
        elif cmd['cmd'] == 'turn_right':
            angle = cmd['args'][0]
            self._heading += angle
        elif cmd['cmd'] == 'turn_left':
            angle = cmd['args'][0]
            self._heading -= angle
        self.screen_update()
