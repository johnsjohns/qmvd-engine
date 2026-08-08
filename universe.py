import random

from particle import Particle


class Universe:
    def __init__(self, width=100, height=100, particle_count=10, seed=666):
        self.width = width
        self.height = height
        self.seed = seed
        self.time = 0

        random.seed(seed)

        self.particles = []

        for particle_id in range(particle_count):
            particle = Particle(
                particle_id,
                self.width,
                self.height
            )

            self.particles.append(particle)

    def tick(self):
        for particle in self.particles:
            particle.move(self.width, self.height)

        self.time += 1

    def run(self, ticks):
        for _ in range(ticks):
            self.tick()

    def status(self):
        print()
        print("=== QMCD ENGINE ===")
        print(f"Seed: {self.seed}")
        print(f"Time: {self.time} ticks")
        print(f"World: {self.width} x {self.height}")
        print(f"Particles: {len(self.particles)}")
        print()

    def list_particles(self):
        for particle in self.particles:
            print(particle)

    def inspect(self, particle_id):
        for particle in self.particles:
            if particle.id == particle_id:
                print(particle)
                return

        print("Partícula não encontrada.")