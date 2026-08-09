import math
import random
from tqdm import tqdm

from particle import Particle
from config import (
    PARTICLE_TYPES,
    INTERACTIONS,
    INTERACTION_RANGE,
    INTERACTION_STRENGTH,
)

class Universe:
    def __init__(self, width=100, height=100, particle_count=10, seed=666):
        self.width = width
        self.height = height
        self.seed = seed
        self.time = 0
        self.collision_count = 0

        random.seed(seed)

        self.particles = []

        type_names = list(PARTICLE_TYPES.keys())

        type_weights = [
            PARTICLE_TYPES[name]["weight"]
            for name in type_names
        ]

        for particle_id in range(particle_count):
            particle_type = random.choices(
                type_names,
                weights=type_weights,
                k=1
            )[0]

            properties = PARTICLE_TYPES[particle_type]

            particle = Particle(
                particle_id,
                self.width,
                self.height,
                particle_type,
                properties["mass"],
                properties["radius"],
            )

            self.particles.append(particle)
        self.initial_total_energy = self.total_energy()
        self.initial_kinetic_energy = self.total_kinetic_energy()

    def tick(self):
        self.apply_interactions()

        for particle in self.particles:
            particle.move(
                self.width,
                self.height
            )

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
        for _ in tqdm(
            range(ticks),
            desc="Simulando",
            unit="tick",
            dynamic_ncols=True,
        ):
            self.tick()

    def status(self):
        print()
        print("=== QMVD ENGINE ===")
        print(f"Seed: {self.seed}")
        print(f"Time: {self.time} ticks")
        print(f"World: {self.width} x {self.height}")
        print(f"Particles: {len(self.particles)}")
        print(f"Collisions: {self.collision_count}")

        kinetic_energy = self.total_kinetic_energy()
        potential_energy = self.total_potential_energy()
        total_energy = kinetic_energy + potential_energy

        energy_drift = (
            total_energy -
            self.initial_total_energy
        )

        momentum_x, momentum_y = self.total_momentum()

        print(f"Kinetic energy:   {kinetic_energy:.9f}")
        print(f"Potential energy: {potential_energy:.9f}")
        print(f"Total energy:     {total_energy:.9f}")
        print(f"Energy drift:     {energy_drift:+.9e}")

        print(
            f"Momentum: "
            f"({momentum_x:.6f}, {momentum_y:.6f})"
)

        counts = self.particle_type_counts()

        print(
            "Types: "
            + ", ".join(
                f"{particle_type}={count}"
                for particle_type, count in sorted(counts.items())
            )
        )
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

    def total_kinetic_energy(self):
        total = 0.0

        for particle in self.particles:
            speed_squared = (
                particle.vx * particle.vx +
                particle.vy * particle.vy
            )

            total += 0.5 * particle.mass * speed_squared

        return total

    def total_momentum(self):
        px = 0.0
        py = 0.0

        for particle in self.particles:
            px += particle.mass * particle.vx
            py += particle.mass * particle.vy

        return px, py

    def particle_type_counts(self):
        counts = {}

        for particle in self.particles:
            counts[particle.type] = (
                counts.get(particle.type, 0) + 1
            )

        return counts

    def apply_interactions(self):
            particle_count = len(self.particles)

            for i in range(particle_count):
                for j in range(i + 1, particle_count):
                    p1 = self.particles[i]
                    p2 = self.particles[j]

                    dx = p2.x - p1.x
                    dy = p2.y - p1.y

                    distance_squared = dx * dx + dy * dy

                    if distance_squared == 0:
                        continue

                    distance = math.sqrt(distance_squared)

                    if distance > INTERACTION_RANGE:
                        continue

                    key = tuple(sorted((p1.type, p2.type)))
                    affinity = INTERACTIONS.get(key, 0.0)

                    if affinity == 0:
                        continue

                    nx = dx / distance
                    ny = dy / distance

                    # Quanto mais perto, maior a interação.
                    distance_factor = 1.0 - (
                        distance / INTERACTION_RANGE
                    )

                    force = (
                        affinity
                        * INTERACTION_STRENGTH
                        * distance_factor
                    )

                    fx = force * nx
                    fy = force * ny

                    # F = m*a  ->  a = F/m
                    p1.vx += fx / p1.mass
                    p1.vy += fy / p1.mass

                    p2.vx -= fx / p2.mass
                    p2.vy -= fy / p2.mass


    def total_potential_energy(self):
        total = 0.0
        particle_count = len(self.particles)

        for i in range(particle_count):
            for j in range(i + 1, particle_count):
                p1 = self.particles[i]
                p2 = self.particles[j]

                dx = p2.x - p1.x
                dy = p2.y - p1.y

                distance = math.sqrt(
                    dx * dx +
                    dy * dy
                )

                if distance >= INTERACTION_RANGE:
                    continue

                key = tuple(sorted((p1.type, p2.type)))
                affinity = INTERACTIONS.get(key, 0.0)

                if affinity == 0:
                    continue

                potential = -(
                    affinity
                    * INTERACTION_STRENGTH
                    * (
                        INTERACTION_RANGE / 2
                        - distance
                        + (distance * distance)
                        / (2 * INTERACTION_RANGE)
                    )
                )

                total += potential

        return total

    def total_energy(self):
        return (
            self.total_kinetic_energy()
            + self.total_potential_energy()
        )
    

    