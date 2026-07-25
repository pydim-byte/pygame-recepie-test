import pygame
from .globals import *


class PlayButton():
    def __init__(self):
        self.text = "PLAY"

    def draw(self, surf):
        font = pygame.font.Font(None, 128)
        text = font.render(self.text, True, 'black')
        textRect = text.get_rect()
        textRect.center = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2

        background_rect = pygame.Rect(textRect[0], textRect[1], textRect[2] + 20, textRect[3] + 20)
        background_rect.center = textRect.center

        pygame.draw.rect(surf, "yellow", background_rect, border_radius=8)
        pygame.draw.rect(surf, "black", background_rect, border_radius=8, width=4)
        surf.blit(text, textRect)