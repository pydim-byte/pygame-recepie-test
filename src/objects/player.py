import pygame
from ..globals import *


class Player(pygame.sprite.Sprite):
    def __init__(self,pos):
        super().__init__()
        self.type = 'player'
        self.size = (36,32)
        self.image = pygame.Surface(self.size, pygame.SRCALPHA)
        self.rotated_image = None
        self.current_image_rotation = 0
        self.rect = self.image.get_rect(topleft = pos)
        self.mask = pygame.mask.from_surface(self.image)

        self.pos = pos
        self.prev_pos = self.pos.copy()
        self.direction = pygame.Vector2(0,1)
        self.vel = pygame.Vector2(0,0)

        self.hp = 1

    def jump(self):
        self.direction.y = PLAYER_JUMP_VEL

    def calculate_velocity(self):
        if self.direction.y < 0:
            self.vel.y += self.direction.y
            self.current_image_rotation = 25
        else:
            self.vel.xy += self.direction.xy
            self.vel.y = min(self.vel.y, PLAYER_TERMINAL_VEL)
            self.current_image_rotation -= 1
        self.rotated_image = pygame.transform.rotate(self.image, self.current_image_rotation)
        self.mask = pygame.mask.from_surface(self.rotated_image)

    def fixed_update(self):
        self.prev_pos.xy = self.pos.xy
        self.direction.y = 1

    def update(self,dt):
        pass

    def draw(self,surf,alpha):
        alpha_pos = self.pos * alpha + self.prev_pos * (1 - alpha)
        draw_rect = self.rect.copy()
        draw_rect.topleft = alpha_pos

        surf_draw_rect = pygame.Rect(0,0,draw_rect.width,draw_rect.height)
        eye_rect = pygame.Rect(surf_draw_rect[0] + 20, surf_draw_rect[1] + 10, surf_draw_rect[2] // 6, surf_draw_rect[2] // 8)
        lip_rect = pygame.Rect(surf_draw_rect[0] + 12, surf_draw_rect[1] + 21, surf_draw_rect[2] - 12, surf_draw_rect[3] // 4)
        lip_line_rect = pygame.Rect(lip_rect[0], lip_rect[1], lip_rect[2], lip_rect[3] // 4)
        lip_line_rect.center = lip_rect.center

        pygame.draw.ellipse(self.image, "yellow", surf_draw_rect)
        pygame.draw.ellipse(self.image, "black", surf_draw_rect, width=2)
        pygame.draw.circle(self.image, "white", eye_rect.center, eye_rect.width)
        pygame.draw.circle(self.image, "black", eye_rect.center, eye_rect.width, width=2)
        pygame.draw.circle(self.image, "black", eye_rect.center, eye_rect.width//3)
        pygame.draw.rect(self.image, "red", lip_rect, border_radius=4)
        pygame.draw.rect(self.image, "black", lip_rect, border_radius=4, width=2)
        pygame.draw.rect(self.image, "black", lip_line_rect, border_radius=4)

        if self.rotated_image is None:
            self.rotated_image = pygame.transform.rotate(self.image, self.current_image_rotation)

        surf.blit(self.rotated_image, draw_rect)
    

    