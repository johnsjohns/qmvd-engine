import math
import random

from particle import Particle


class Universe:
    def __init__(self, width=100, height=100, particle_count=10, seed=666):
        self.width = width
        self.height = height
        self.seed = seed
        self.time = 0
        self.collision_count = 0

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
        # Primeiro movimentamos as partículas
        for particle in self.particles:
            particle.move(self.width, self.height)

        # Depois verificamos colisões
        self.handle_collisions()

        self.time += 1

    def handle_collisions(self):
        particle_count = len(self.particles)

        for i in range(particle_count):
            for j in range(i + 1, particle_count):
                p1 = self.particles[i]
                p2 = self.particles[j]

                dx = p2.x - p1.x
                dy = p2.y - p1.y

                distance_squared = dx * dx + dy * dy
                min_distance = p1.radius + p2.radius

                if distance_squared <= min_distance * min_distance:
                    self.resolve_collision(p1, p2)

    def resolve_collision(self, p1, p2):
        dx = p2.x - p1.x
        dy = p2.y - p1.y

        distance = math.sqrt(dx * dx + dy * dy)

        # Caso extremamente raro:
        # duas partículas exatamente no mesmo ponto
        if distance == 0:
            dx = 0.01
            dy = 0.0
            distance = 0.01

        # Vetor normal da colisão
        nx = dx / distance
        ny = dy / distance

        # Velocidade relativa
        relative_vx = p2.vx - p1.vx
        relative_vy = p2.vy - p1.vy

        # Velocidade relativa ao longo da normal
        velocity_along_normal = (
            relative_vx * nx +
            relative_vy * ny
        )

        # Se já estão se afastando,
        # não aplicamos outra colisão
        if velocity_along_normal > 0:
            self.correct_overlap(p1, p2, nx, ny, distance)
            return

        # Coeficiente de restituição
        # 1.0 = colisão perfeitamente elástica
        restitution = 1.0

        impulse = -(
            (1 + restitution) *
            velocity_along_normal
        )

        impulse /= (
            (1 / p1.mass) +
            (1 / p2.mass)
        )

        impulse_x = impulse * nx
        impulse_y = impulse * ny

        # Aplicar impulso
        p1.vx -= impulse_x / p1.mass
        p1.vy -= impulse_y / p1.mass

        p2.vx += impulse_x / p2.mass
        p2.vy += impulse_y / p2.mass

        # Corrigir sobreposição
        self.correct_overlap(
            p1,
            p2,
            nx,
            ny,
            distance
        )

        self.collision_count += 1

    def correct_overlap(self, p1, p2, nx, ny, distance):
        min_distance = p1.radius + p2.radius
        overlap = min_distance - distance

        if overlap <= 0:
            return

        correction = overlap / 2

        p1.x -= nx * correction
        p1.y -= ny * correction

        p2.x += nx * correction
        p2.y += ny * correction

    def run(self, ticks):
        for _ in range(ticks):
            self.tick()

    def status(self):
        print()
        print("=== QMVD ENGINE ===")
        print(f"Seed: {self.seed}")
        print(f"Time: {self.time} ticks")
        print(f"World: {self.width} x {self.height}")
        print(f"Particles: {len(self.particles)}")
        print(f"Collisions: {self.collision_count}")
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