import random


class Particle:
    def __init__(self, particle_id, world_width, world_height):
        self.id = particle_id

        self.radius = 1.0
        self.mass = 1.0

        self.x = random.uniform(self.radius, world_width - self.radius)
        self.y = random.uniform(self.radius, world_height - self.radius)

        self.vx = random.uniform(-1, 1)
        self.vy = random.uniform(-1, 1)

    def move(self, world_width, world_height):
        self.x += self.vx
        self.y += self.vy

        # Parede esquerda
        if self.x - self.radius < 0:
            self.x = self.radius
            self.vx *= -1

        # Parede direita
        elif self.x + self.radius > world_width:
            self.x = world_width - self.radius
            self.vx *= -1

        # Parede inferior
        if self.y - self.radius < 0:
            self.y = self.radius
            self.vy *= -1

        # Parede superior
        elif self.y + self.radius > world_height:
            self.y = world_height - self.radius
            self.vy *= -1

    def __str__(self):
        return (
            f"Particle #{self.id} | "
            f"Pos=({self.x:.2f}, {self.y:.2f}) | "
            f"Vel=({self.vx:.2f}, {self.vy:.2f}) | "
            f"Mass={self.mass:.2f} | "
            f"Radius={self.radius:.2f} | "
            f"KineticE={self.kinetic_energy:.4f}"
        )

    @property
    def kinetic_energy(self):
        return 0.5 * self.mass * (
            self.vx * self.vx +
            self.vy * self.vy
        )