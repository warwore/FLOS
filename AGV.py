import pygame
from sys import exit
import numpy as np

class AGV:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed
        self.start_pos = (x, y)
        self.surf = pygame.image.load('graphics/agv.png').convert_alpha()
        self.surf = pygame.transform.scale(self.surf, (20, 20))
        self.rect = self.surf.get_rect(topleft=self.start_pos)
        self.camera_offset = 10
        self.cam_x = self.x + self.camera_offset
        self.cam_y = self.y + self.camera_offset
        self.camera_length = 10
        self.direction = 'right'

    def move(self, drawing, color):
        if not drawing and color == 215:
            self.rect.x += 1
            self.cam_x += 1