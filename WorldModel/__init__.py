import math
from math import sin, cos

from point2d import Point2D
import pygame

'''
    Internal world model from the point of view of the robot
    Used for mapping and/or basic SLAM
'''
# on v-rep the robot with an angular speed of 1 rad/s should move in 1 sec of about 9.4 cm. GPU_FACTOR = VREP_covered_distance_cm / 9.4
# on v-rep the robot with an angular speed of 1 rad/s should rotate in 1 sec of an angle of about 32 degrees.
GPU_FACTOR = 1  # on other platforms could be necessary to adapt this factor to get correct values of robot movements
WORLD_SIZE = 500  # px
WHEEL_RADIUS = 0.094 * GPU_FACTOR # meters
HALF_ROBOT_WIDTH = 0.165  # meters - half pioneer width
SENSOR_DISTANCE = 0.25  # meters - distance between robot center and visor
SLEEP_TIME = 2
REAL_SPACE_SPAN = 5  # meters -  same size of vrep scene
ORIGIN = [int(WORLD_SIZE / 2), int(WORLD_SIZE / 2)]
BLACK = (0, 0, 0)
GREY = (100, 100, 100)
RESOLUTION = REAL_SPACE_SPAN / WORLD_SIZE  # meters x pixel 0.1 mxp ---> 1px = 1cm
GRID = 10  # grid 10 x 10
MIN_BOTTLE_HEIGHT = 0.11  # meters. threshold, it is a bit more than half height of the bottle
MIN_BOTTLE_HEIGHT_perceived = 0.05
PROXIMITY_VISION_DISTANCE = 0.08  # meters. it is the x axis distance between proximity sensor and vision sensor
CENTERS_GAP = 0.05  # meters. gap between robot center and rotation center
MAX_ROW_VOTING_TABLE = 500  # the maximum number of row of voting_table
HEADING_FROM_COMPASS = False
OSD = False  # on screen display info: robot position and orientation


class WorldModel:

    def __init__(self):
        pygame.init()
        self._screen = pygame.display.set_mode((WORLD_SIZE, WORLD_SIZE))
        self._screen.fill(BLACK)
        # draw grid
        for column in range(1, GRID):
            pygame.draw.line(self._screen, GREY, (WORLD_SIZE * column / GRID, 0),
                             (WORLD_SIZE * column / GRID, WORLD_SIZE))
            pygame.draw.line(self._screen, GREY, (0, WORLD_SIZE * column / GRID),
                             (WORLD_SIZE, WORLD_SIZE * column / GRID))
        self._sprite = pygame.image.load('graphics/cross8x8.png')
        self._obstacle_sprite = pygame.image.load('graphics/obstacle.png')
        self._bottle_sprite = pygame.image.load('graphics/bottle.png')
        self._rect = self._sprite.get_rect()
        self._position = [ORIGIN[0], ORIGIN[1]]
        self._translation = [0.0, 0.0]
        self._heading = 0
        self._rect = self._rect.move(self._position[0] - 4, self._position[1] - 4)
        self._last_cmd = ''
        self._voting_table = list()
        self.screen_update()

    def move(self):
        self._position[0] += self._translation[0]
        self._position[1] += self._translation[1]
        self._rect = self._rect.move(self._translation)
        print(38, self._position, self._translation, self._rect)

    def screen_update(self, obstacle_rect=[], bottle_rect=None):
        self.move()
        self._screen.blit(self._sprite, self._rect)

        if OSD:
            font = pygame.font.SysFont('arial', 12)
            self._screen.blit(font.render([(round(self._position[0], 2), round(self._position[1], 2)),
                                           round((180 + math.degrees(self._heading)), 2)].__str__(), True, (0, 255, 0),
                                          (0, 0, 0)), self._rect.move(10, 0))

        for obs in obstacle_rect:
            self._screen.blit(self._obstacle_sprite, obs)

        if bottle_rect:
            # print("bottle: ", bottle_rect)
            self._screen.blit(self._bottle_sprite, bottle_rect)

        pygame.display.update()

    def robot_updates(self, commands, percepts):
        '''
        :param percepts: new percepts from the robot from which it updates its
                internal world representation
        :return:
        '''
        obstacle_list = []
        bottle_rect = None

        if HEADING_FROM_COMPASS:
            self._heading = math.pi + percepts["compass"]

        if len(commands) > 0:
            cmd = commands[0]
        else:
            cmd = self._last_cmd

        if cmd['cmd'] == 'move_forward':
            print("arg", cmd['args'][0])
            linear_speed = ((cmd['args'][0] * WHEEL_RADIUS) / RESOLUTION)  # in pixels x second
            print("linear_speed ", linear_speed)
            print("heading ", math.degrees(self._heading), " | ", self._heading)
            # axis rotated by -pi/2
            self._translation = (
                SLEEP_TIME * linear_speed * sin(self._heading), SLEEP_TIME * linear_speed * cos(self._heading))

            if percepts:
                print("Percepts :", percepts)

                center_right_dis = percepts["center_right"][0]
                center_left_dis = percepts["center_left"][0]
                left_dis = percepts["left"][0]
                right_dis = percepts["right"][0]
                obstacle_list.clear()

                sensor_name = percepts["vision"][0]
                height_bottle_perceived = percepts["vision"][3]  # bottle_height

                if center_left_dis < 0.9999:
                    print("solo center_left ")
                    print("obstacle distance: ", center_left_dis, "heading: ", self._heading)

                    if not percepts["center_left"][1].get_z():
                        alpha = 0
                    else:
                        # angle between central sensor axis and sensor-perception_point line
                        alpha = math.atan(percepts["center_left"][1].get_x() / percepts["center_left"][1].get_z())

                    # TODO: la seconda condizione può essere inutile dato l'inserimento della terza condizione??
                    if sensor_name == "center_left" and height_bottle_perceived > MIN_BOTTLE_HEIGHT_perceived and height_bottle_perceived * 2 * (
                            center_left_dis + PROXIMITY_VISION_DISTANCE) > MIN_BOTTLE_HEIGHT:
                        bottle_rect = list(self._rect)
                        # x-axis pygame
                        bottle_rect[0] += (SENSOR_DISTANCE + center_left_dis) * sin(
                            self._heading + alpha + math.radians(10)) * 1 / RESOLUTION
                        # y-axis pygame
                        bottle_rect[1] += (SENSOR_DISTANCE + center_left_dis) * cos(
                            self._heading + alpha + math.radians(10)) * 1 / RESOLUTION
                    else:
                        obstacle_list.append(list(self._rect))
                        # x-axis pygame
                        obstacle_list[-1][0] += (SENSOR_DISTANCE + center_left_dis) * sin(
                            self._heading + alpha + math.radians(10)) * 1 / RESOLUTION
                        # y-axis pygame
                        obstacle_list[-1][1] += (SENSOR_DISTANCE + center_left_dis) * cos(
                            self._heading + alpha + math.radians(10)) * 1 / RESOLUTION

                if center_right_dis < 0.9999:
                    print("solo center_right ")
                    print("obstacle distance: ", center_right_dis, "heading: ", self._heading)

                    if not percepts["center_right"][1].get_z():
                        alpha = 0
                    else:
                        # angle between central sensor axis and sensor-perception_point line
                        alpha = math.atan(percepts["center_right"][1].get_x() / percepts["center_right"][1].get_z())

                    if sensor_name == "center_right" and height_bottle_perceived > MIN_BOTTLE_HEIGHT_perceived and height_bottle_perceived * 2 * (
                            center_right_dis + PROXIMITY_VISION_DISTANCE) > MIN_BOTTLE_HEIGHT:
                        bottle_rect = list(self._rect)
                        # x-axis pygame
                        bottle_rect[0] += (SENSOR_DISTANCE + center_right_dis) * sin(
                            self._heading + alpha - math.radians(10)) * 1 / RESOLUTION
                        # y-axis pygame
                        bottle_rect[1] += (SENSOR_DISTANCE + center_right_dis) * cos(
                            self._heading + alpha - math.radians(10)) * 1 / RESOLUTION
                    else:
                        obstacle_list.append(list(self._rect))
                        # x-axis pygame
                        obstacle_list[-1][0] += (SENSOR_DISTANCE + center_right_dis) * sin(
                            self._heading + alpha - math.radians(10)) * 1 / RESOLUTION
                        # y-axis pygame
                        obstacle_list[-1][1] += (SENSOR_DISTANCE + center_right_dis) * cos(
                            self._heading + alpha - math.radians(10)) * 1 / RESOLUTION

                if left_dis < 0.9999:
                    print("solo left ")
                    print("obstacle left distance: ", left_dis, "heading: ", self._heading)

                    if not percepts["left"][1].get_z():
                        alpha = 0
                    else:
                        # angle between central sensor axis and sensor-perception_point line
                        alpha = math.atan(percepts["left"][1].get_x() / percepts["left"][1].get_z())

                    if sensor_name == "left" and height_bottle_perceived > MIN_BOTTLE_HEIGHT_perceived and height_bottle_perceived * 2 * (
                            left_dis + PROXIMITY_VISION_DISTANCE) > MIN_BOTTLE_HEIGHT:
                        bottle_rect = list(self._rect)
                        # x-axis pygame
                        bottle_rect[0] += (SENSOR_DISTANCE + left_dis) * sin(
                            self._heading + alpha + math.radians(30)) * 1 / RESOLUTION
                        # y-axis pygame
                        bottle_rect[1] += (SENSOR_DISTANCE + left_dis) * cos(
                            self._heading + alpha + math.radians(30)) * 1 / RESOLUTION

                    else:
                        obstacle_list.append(list(self._rect))
                        # x-axis pygame
                        obstacle_list[-1][0] += (SENSOR_DISTANCE + left_dis) * sin(
                            self._heading + alpha + math.radians(30)) * 1 / RESOLUTION
                        # y-axis pygame
                        obstacle_list[-1][1] += (SENSOR_DISTANCE + left_dis) * cos(
                            self._heading + alpha + math.radians(30)) * 1 / RESOLUTION

                if right_dis < 0.9999:
                    print("solo right ")
                    print("obstacle right distance: ", right_dis, "heading: ", self._heading)

                    if not percepts["right"][1].get_z():
                        alpha = 0
                    else:
                        # angle between central sensor axis and sensor-perception_point line
                        alpha = math.atan(percepts["right"][1].get_x() / percepts["right"][1].get_z())

                    if sensor_name == "right" and height_bottle_perceived > MIN_BOTTLE_HEIGHT_perceived and \
                            height_bottle_perceived * 2 * (right_dis + PROXIMITY_VISION_DISTANCE) > MIN_BOTTLE_HEIGHT:
                        bottle_rect = list(self._rect)
                        # x-axis pygame
                        bottle_rect[0] += (SENSOR_DISTANCE + right_dis) * sin(
                            self._heading + alpha - math.radians(30)) * 1 / RESOLUTION
                        # y-axis pygame
                        bottle_rect[1] += (SENSOR_DISTANCE + right_dis) * cos(
                            self._heading + alpha - math.radians(30)) * 1 / RESOLUTION

                    else:
                        obstacle_list.append(list(self._rect))
                        # x-axis pygame
                        obstacle_list[-1][0] += (SENSOR_DISTANCE + right_dis) * sin(
                            self._heading + alpha - math.radians(30)) * 1 / RESOLUTION
                        # y-axis pygame
                        obstacle_list[-1][1] += (SENSOR_DISTANCE + right_dis) * cos(
                            self._heading + alpha - math.radians(30)) * 1 / RESOLUTION

                if bottle_rect:  # a bottle has been detected
                    for obs in obstacle_list:
                        # 10% tollerance
                        if math.isclose(obs[0], bottle_rect[0], rel_tol=0.10, abs_tol=0.0) and math.isclose(obs[1],
                                                                                                            bottle_rect[
                                                                                                                1],
                                                                                                            rel_tol=0.10,
                                                                                                            abs_tol=0.0):
                            obstacle_list.remove(obs)

        elif cmd['cmd'] == 'turn_right':
            angular_speed = cmd['args'][0]
            print("angular_speed ", angular_speed)
            self._heading -= (angular_speed * WHEEL_RADIUS * SLEEP_TIME) / HALF_ROBOT_WIDTH

            if not HEADING_FROM_COMPASS:
                # fine adjustment: center of the robot doesn't perfectly overlap center of rotation
                # if last command was turn left and now the robot is turning right set previous position
                if self._last_cmd != '' and self._last_cmd['cmd'] == 'turn_left':
                    self._translation = (- self._translation[0], - self._translation[1])
                else:
                    self._translation = (0, 0)
                    self._translation = (
                        CENTERS_GAP * 1 / RESOLUTION * cos(self._heading),
                        - CENTERS_GAP * 1 / RESOLUTION * sin(self._heading))
            print("heading ", math.degrees(self._heading), " | ", self._heading)

        elif cmd['cmd'] == 'turn_left':

            angular_speed = cmd['args'][0]
            print("angular_speed ", angular_speed)
            self._heading += (angular_speed * WHEEL_RADIUS * SLEEP_TIME) / HALF_ROBOT_WIDTH

            if not HEADING_FROM_COMPASS:
                # fine adjustment: center of the robot doesn't perfectly overlap center of rotation
                if self._last_cmd != '' and self._last_cmd['cmd'] == 'turn_right':
                    self._translation = (- self._translation[0], - self._translation[1])
                else:
                    self._translation = (0, 0)
                    self._translation = (
                        -CENTERS_GAP * 1 / RESOLUTION * cos(self._heading),
                        CENTERS_GAP * 1 / RESOLUTION * sin(self._heading))
            print("heading ", math.degrees(self._heading), " | ", self._heading)

        if bottle_rect:
            p = Point2D(bottle_rect[0], bottle_rect[1])
            already_perceived = False
            for row in self._voting_table:
                if (p - row[0]).r < 5:
                    already_perceived = True
                    row[2] += 1
                    if row[1] > row[2]:
                        bottle_rect = None
                if already_perceived: break

            if not already_perceived:
                if len(self._voting_table) >= MAX_ROW_VOTING_TABLE:
                    self._voting_table.pop(0)
                self._voting_table.append([Point2D(bottle_rect[0], bottle_rect[1]), 0,
                                           1])  # point, times that the point has been perceived as WALL, times that the point has been perceived as BOTTLE

        for obs in obstacle_list:
            p = Point2D(obs[0], obs[1])
            already_perceived = False
            for row in self._voting_table:
                if (p - row[0]).r < 10:
                    already_perceived = True
                    row[1] += 1
                    if row[1] <= row[2]:
                        obstacle_list.remove(obs)
                if already_perceived: break

            if not already_perceived:
                if len(self._voting_table) >= MAX_ROW_VOTING_TABLE:
                    self._voting_table.pop(0)
                self._voting_table.append(
                    [Point2D(obs[0], obs[1]), 1, 0])

        print("VOTING: ", self._voting_table)
        self._last_cmd = cmd
        self.screen_update(obstacle_list, bottle_rect)
