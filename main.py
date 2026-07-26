import pygame, sys, random, os
from src.globals import *
from src.world import World
from src.player_controller import PlayerController
from src.physic_manager import PhysicManager
from src.states import States
from src.score import Score
from src.play_button import PlayButton
from src.retry_button import RetryButton
from jnius import autoclass


class Game:
    def __init__(self):
        #self.hide_system_bars()
        pygame.init()
        pygame.mixer.init()

        path = os.path.abspath(".")+"/"

        self.player_hit_sound = pygame.mixer.Sound(path+"assets/audio/hit.ogg")
        self.score_sound = pygame.mixer.Sound(path+"assets/audio/score.wav")

        self.jump_sounds = []
        self.jump_sound_1 = pygame.mixer.Sound(path+"assets/audio/jump_1.wav")
        self.jump_sound_2 = pygame.mixer.Sound(path+"assets/audio/jump_2.wav")
        self.jump_sound_3 = pygame.mixer.Sound(path+"assets/audio/jump_3.wav")
        self.jump_sounds.append(self.jump_sound_1)
        self.jump_sounds.append(self.jump_sound_2)
        self.jump_sounds.append(self.jump_sound_3)

        self.display = pygame.display.set_mode((DISPLAY_WIDTH,DISPLAY_HEIGHT), pygame.SCALED|pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()
        self.inputs = {pygame.K_LEFT : False, pygame.K_RIGHT : False, pygame.K_UP : False, pygame.K_DOWN : False, pygame.K_SPACE : False, pygame.K_r : False}
        self.world = World()
        self.score = Score()
        self.play_button = PlayButton()
        self.retry_button = RetryButton()
        self.player_controller = PlayerController(self.world.player.sprite)
        self.physic_manager = PhysicManager(self.world)
        self.state = States.START

    def hide_system_bars(self):
        try:
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            View = autoclass('android.view.View')
            activity = PythonActivity.mActivity
            window = activity.getWindow()
            decor_view = window.getDecorView()
            decor_view.setSystemUiVisibility(
                View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
                | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
                | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                | View.SYSTEM_UI_FLAG_FULLSCREEN
                | View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
            )
        except Exception as e:
            print(f"Could not hide system bars: {e}")

    def handle_events(self,event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.state == States.START:
                self.state = States.GAMEPLAY
            if self.state == States.GAMEPLAY:
                random.choice(self.jump_sounds).play() 
                self.world.player.sprite.jump()
            if self.state == States.RETRY:
                self.world = World()
                self.player_controller = PlayerController(self.world.player.sprite)
                self.physic_manager = PhysicManager(self.world)
                self.score.score = 0
                self.state = States.GAMEPLAY
        if event.type in [pygame.KEYUP, pygame.KEYDOWN]:
            self.handle_key_events(event) 

    def handle_key_events(self, event):
        if event.type == pygame.KEYDOWN:
            for inpput_key in self.inputs:
                if event.key == inpput_key:
                    self.inputs[inpput_key] = True

        if event.type == pygame.KEYUP:
            for inpput_key in self.inputs:
                if event.key == inpput_key:
                    self.inputs[inpput_key] = False

    def handle_inputs(self):
        self.player_controller.handle_inputs(self.inputs)
        if self.state == States.GAMEPLAY and self.inputs[pygame.K_SPACE]:
            random.choice(self.jump_sounds).play() 
        if self.state == States.START and self.inputs[pygame.K_SPACE]:
            self.state = States.GAMEPLAY
        if self.state == States.RETRY and self.inputs[pygame.K_r]:
            self.world = World()
            self.player_controller = PlayerController(self.world.player.sprite)
            self.physic_manager = PhysicManager(self.world)
            self.score.score = 0
            self.state = States.GAMEPLAY
        self.inputs = {k:False for k in self.inputs}

    def fixed_update(self):
        if self.state != States.GAMEPLAY:
            return
        self.physic_manager.fixed_update()
        for obj in self.world.physical_objects:
            obj.fixed_update()
        pipe_counter = 0
        for pipe in self.world.pipes:
            if pipe.rect.x <= self.world.player.sprite.rect.x and not pipe.reached:
                pipe_counter += 1
                pipe.reached = True
        if pipe_counter >= 2:
            self.score.score += 1
            if self.score.score > self.score.hight_score:
                self.score.hight_score = self.score.score
            self.score_sound.play()
        if any ([self.world.player.sprite.rect.y < 0,
                self.world.player.sprite.rect.bottom > SCREEN_HEIGHT,
                self.world.player.sprite.hp <= 0]):
            self.state = States.RETRY
            self.player_hit_sound.play()
            return
 
    def update(self,dt):
        if self.state != States.GAMEPLAY:
            return
        self.world.update(dt)
        self.world.all_sprites.update(dt)

    def draw(self,alpha):
        self.display.fill((130,200,229))
        for sprite in self.world.all_sprites:
            sprite.draw(self.display,alpha)
        self.score.draw(self.display)
        if self.state == States.START:
            self.play_button.draw(self.display)
        if self.state == States.RETRY:
            self.retry_button.draw(self.display)
        pygame.display.flip()

    def run(self):
        accumulator = 0
        while True:
            dt = self.clock.tick(FPS) / 1000
            dt = min(dt,0.1)
            accumulator += dt

            while accumulator >= dt:
                for event in pygame.event.get(): self.handle_events(event)
                self.handle_inputs()
                self.fixed_update()
                accumulator -= 1/FIXED_TPS

            alpha = accumulator / dt

            self.update(dt)
            self.draw(alpha)

game = Game()
game.run()
