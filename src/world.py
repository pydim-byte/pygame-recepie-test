import pygame, random
from .globals import *
from .objects.pipe import Pipe
from .objects.player import Player


class World:
    def __init__(self):
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.physical_objects = pygame.sprite.Group()
        self.pipes = pygame.sprite.Group()
        self.player = pygame.sprite.GroupSingle()
        self.first_pipe_generated = False
        self.generate_pipes()
        self.get_player()
        self.pipe_clock = {"current_wait_time" : 0, "max_wait_time" : 0.5}

    def generate_pipes(self):
        pipe_x = SCREEN_WIDTH - PIPE_WIDTH
        
        if self.first_pipe_generated:
            sorted_pipes = sorted(list(self.pipes), key=lambda pipe : pipe.rect.x)
            pipe_x = sorted_pipes[-1].rect.right + PIPE_WIDTH * 4

        pipe_1_pos = pygame.Vector2(pipe_x, 0)
        pipe_1_height = random.randint(MIN_PIPE_HEIGHT, MAX_PIPE_HEIGHT)
        pipe_1_size = (PIPE_WIDTH, pipe_1_height)

        pipe_2_pos = pygame.Vector2(pipe_x, pipe_1_height + PIPE_GAP)
        pipe_2_height = SCREEN_HEIGHT - pipe_1_height - PIPE_GAP
        pipe_2_size = (PIPE_WIDTH, pipe_2_height)

        self.pipes.add(Pipe(pipe_1_pos,pipe_1_size))
        self.pipes.add(Pipe(pipe_2_pos,pipe_2_size))
        
        self.all_sprites.add(self.pipes, layer=1)
        self.physical_objects.add(self.pipes)

        self.first_pipe_generated = True

    def get_player(self):
        pos = pygame.Vector2(SCREEN_WIDTH//4, SCREEN_HEIGHT//2)
        self.player.add(Player(pos))
        self.all_sprites.add(self.player, layer=2)
        self.physical_objects.add(self.player)

    def update(self,dt):
        if self.pipe_clock["current_wait_time"] >= self.pipe_clock["max_wait_time"]:
            self.pipe_clock["current_wait_time"] = 0
            self.generate_pipes()
        self.pipe_clock["current_wait_time"] += dt
        for pipe in self.pipes:
            if pipe.rect.right < -10:
                pipe.kill()