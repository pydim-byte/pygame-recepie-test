import pygame
from .objects.player import Player


class PlayerController:
    def __init__(self,player : Player):
        self.player = player

    def handle_inputs(self,inputs):
        if inputs[pygame.K_SPACE]:
            self.player.jump()