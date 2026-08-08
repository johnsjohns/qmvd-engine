import random


class Particle:
    def __init__(self, particle_id, world_width, world_height):
        self.id = particle_id

        self.x = random.uniform(0, world_width)
        self.y = random.uniform(0, world_height)

        self.vx = random.uniform(-1, 1)
        self.vy = random.uniform(-1, 1)

        self.mass = 1.0
        self.energy = 1.0

    def move(self, world_width, world_height):
        self.x += self.vx
        self.y += self.vy

        if self.x < 0:
            self.x = 0
            self.vx *= -1

        elif self.x > world_width:
            self.x = world_width
            self.vx *= -1

        if self.y < 0:
            self.y = 0
            self.vy *= -1

        elif self.y > world_height:
            self.y = world_height
            self.vy *= -1

    def __str__(self):
        return (
            f"Particle #{self.id} | "
            f"Pos=({self.x:.2f}, {self.y:.2f}) | "
            f"Vel=({self.vx:.2f}, {self.vy:.2f}) | "
            f"Mass={self.mass:.2f} | "
            f"Energy={self.energy:.2f}"
        )