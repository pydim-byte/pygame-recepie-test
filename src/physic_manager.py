import pygame
from .world import World


class PhysicManager:
    def __init__(self, world : World):
        self.physical_objects = world.physical_objects
    
    def move_horizontal(self,obj):
        obj.rect.x += obj.vel.x
        obj.pos.x = obj.rect.x

    def move_vertical(self,obj):
        obj.rect.y += obj.vel.y
        obj.pos.y = obj.rect.y

    def check_collisions(self,obj):
        if obj.type != "player":
            return
        for collision_obj in self.physical_objects:
            if collision_obj == obj:
                continue
            if pygame.sprite.collide_mask(obj, collision_obj):
                obj.hp -= 1

    def move_and_collide(self,obj):
        if not obj.alive():
            return

        obj.calculate_velocity()
        self.move_horizontal(obj)
        self.move_vertical(obj)
        self.check_collisions(obj)

    def fixed_update(self):
        for obj in self.physical_objects:
            self.move_and_collide(obj)