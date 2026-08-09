import random
from config import TIME_STEP

class Particle:
    def __init__(
        self,
        particle_id,
        world_width,
        world_height,
        particle_type,
        mass,
        radius,
    ):
        self.id = particle_id
        self.type = particle_type

        self.mass = mass
        self.radius = radius

        self.x = random.uniform(
            self.radius,
            world_width - self.radius
        )

        self.y = random.uniform(
            self.radius,
            world_height - self.radius
        )

        self.vx = random.uniform(-1, 1)
        self.vy = random.uniform(-1, 1)
        self.ax = 0.0
        self.ay = 0.0

    @property
    def kinetic_energy(self):
        speed_squared = (
            self.vx * self.vx +
            self.vy * self.vy
        )

        return 0.5 * self.mass * speed_squared

    def move(self, world_width, world_height):
        self.x += self.vx * TIME_STEP
        self.y += self.vy * TIME_STEP

        if self.x - self.radius < 0:
            self.x = self.radius
            self.vx *= -1

        elif self.x + self.radius > world_width:
            self.x = world_width - self.radius
            self.vx *= -1

        if self.y - self.radius < 0:
            self.y = self.radius
            self.vy *= -1

        elif self.y + self.radius > world_height:
            self.y = world_height - self.radius
            self.vy *= -1

    def __str__(self):
        return (
            f"Particle #{self.id} | "
            f"Type={self.type} | "
            f"Pos=({self.x:.2f}, {self.y:.2f}) | "
            f"Vel=({self.vx:.2f}, {self.vy:.2f}) | "
            f"Mass={self.mass:.2f} | "
            f"Radius={self.radius:.2f} | "
            f"KineticE={self.kinetic_energy:.4f}"
        )