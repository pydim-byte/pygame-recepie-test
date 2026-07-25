import pygame
from ..globals import *


class Pipe(pygame.sprite.Sprite):
    def __init__(self,pos,size):
        super().__init__()
        self.type = 'pipe'
        self.image = pygame.surface.Surface(size)
        self.image.fill("green")
        self.rect = self.image.get_rect(topleft = pos)
        self.mask = pygame.mask.from_surface(self.image)

        self.reached = False

        self.pos = pos
        self.prev_pos = self.pos.copy()
        self.direction = pygame.Vector2(-1,0)
        self.vel = pygame.Vector2(0,0)

    def calculate_velocity(self):
        self.vel.x = self.direction.x * PIPE_SPEED

    def fixed_update(self):
        self.prev_pos.xy = self.pos.xy

    def update(self,dt):
        pass

    def draw(self,surf,alpha):
        alpha_pos = self.pos * alpha + self.prev_pos * (1 - alpha)
        draw_rect = self.rect.copy()
        draw_rect.topleft = alpha_pos

        outline_rect = pygame.Rect(draw_rect[0], draw_rect[1], draw_rect[2] + 4, draw_rect[3] + 4)
        outline_rect.center = draw_rect.center

        pygame.draw.rect(surf, "black", outline_rect)
        pygame.draw.rect(surf, "green", draw_rect)
        

    