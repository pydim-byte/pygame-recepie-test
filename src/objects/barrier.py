import pygame


class Barrier:
    def __init__(self,x,y,width,height):
        self.type = 'barrier'
        self.rect = pygame.Rect(x,y,width,height)

    def alive(self):
        return True