import pygame
from .globals import *


class Score():
    def __init__(self):
        self.score = 0
        self.hight_score = 0

    def draw(self, surf):
        font_small = pygame.font.Font(None, 36)
        font_big = pygame.font.Font(None, 72)

        hight_score_text = font_small.render(f"{self.hight_score}", True, 'black')
        hight_score_text_rect = hight_score_text.get_rect()
        hight_score_text_rect.centerx = SCREEN_WIDTH // 2
        hight_score_text_rect.top = 10

        current_score_text = font_big.render(f"{self.score}", True, 'black')
        current_score_text_rect = current_score_text.get_rect()
        current_score_text_rect.centerx = SCREEN_WIDTH // 2
        current_score_text_rect.top = hight_score_text_rect.bottom

        surf.blit(hight_score_text, hight_score_text_rect)
        surf.blit(current_score_text, current_score_text_rect)