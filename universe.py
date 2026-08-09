import math
import random
from tqdm import tqdm
from particle import Particle
from config import (
     PARTICLE_TYPES,
    INTERACTIONS,
    INTERACTION_RANGE,
    INTERACTION_STRENGTH,
    TIME_STEP,
    HARD_COLLISIONS_ENABLED,
    REPULSION_RANGE_FACTOR,
    REPULSION_STRENGTH,
    WALLS_ENABLED,
WALL_REPULSION_RANGE,
WALL_REPULSION_STRENGTH,
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
        dt = TIME_STEP

        # 1. Calcula acelerações no estado atual
        self.calculate_accelerations()

        # 2. Atualiza posição usando velocidade
        #    e metade da aceleração
        for particle in self.particles:
            particle.x += (
                particle.vx * dt
                + 0.5 * particle.ax * dt * dt
            )

            particle.y += (
                particle.vy * dt
                + 0.5 * particle.ay * dt * dt
            )

            # Metade da atualização da velocidade
            particle.vx += 0.5 * particle.ax * dt
            particle.vy += 0.5 * particle.ay * dt
            if WALLS_ENABLED:
                self.handle_wall_collision(particle)

        # Colisões partícula-partícula
        if HARD_COLLISIONS_ENABLED:
            self.handle_collisions()

        # 3. Recalcula acelerações nas novas posições
        self.calculate_accelerations()

        # 4. Completa a atualização da velocidade
        for particle in self.particles:
            particle.vx += 0.5 * particle.ax * dt
            particle.vy += 0.5 * particle.ay * dt

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

        inverse_mass_1 = 1.0 / p1.mass
        inverse_mass_2 = 1.0 / p2.mass

        inverse_mass_sum = (
            inverse_mass_1 +
            inverse_mass_2
        )

        if inverse_mass_sum == 0:
            return

        correction_1 = (
            overlap
            * inverse_mass_1
            / inverse_mass_sum
        )

        correction_2 = (
            overlap
            * inverse_mass_2
            / inverse_mass_sum
        )

        p1.x -= nx * correction_1
        p1.y -= ny * correction_1

        p2.x += nx * correction_2
        p2.y += ny * correction_2

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
        print(f"Time step: {TIME_STEP}")
        print(f"Simulation time: {self.time * TIME_STEP:.3f}")

        print(f"World: {self.width} x {self.height}")
        print(f"Particles: {len(self.particles)}")
        print(f"Collisions: {self.collision_count}")

        kinetic_energy = self.total_kinetic_energy()
        particle_potential = self.total_potential_energy()
        wall_potential = self.wall_potential_energy()

        total_energy = (
            kinetic_energy
            + particle_potential
            + wall_potential
        )

        energy_drift = (
            total_energy
            - self.initial_total_energy
        )

        momentum_x, momentum_y = self.total_momentum()

        print()
        print(f"Kinetic energy:        {kinetic_energy:.9f}")
        print(f"Particle potential:    {particle_potential:.9f}")
        print(f"Wall potential:        {wall_potential:.9f}")
        print(f"Total energy:          {total_energy:.9f}")
        print(f"Energy drift:          {energy_drift:+.9e}")

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

   

    def calculate_accelerations(self):
        # ---------------------------------
        # ZERAR ACELERAÇÕES
        # ---------------------------------

        for particle in self.particles:
            particle.ax = 0.0
            particle.ay = 0.0

        particle_count = len(self.particles)

        # ---------------------------------
        # INTERAÇÕES PARTÍCULA-PARTÍCULA
        # ---------------------------------

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

                nx = dx / distance
                ny = dy / distance

                total_force = 0.0

                # -----------------------------
                # Afinidade entre tipos
                # -----------------------------

                if distance < INTERACTION_RANGE:
                    key = tuple(sorted((p1.type, p2.type)))
                    affinity = INTERACTIONS.get(key, 0.0)

                    if affinity != 0:
                        distance_factor = (
                            1.0
                            - distance / INTERACTION_RANGE
                        )

                        interaction_force = (
                            affinity
                            * INTERACTION_STRENGTH
                            * distance_factor
                        )

                        total_force += interaction_force

                # -----------------------------
                # Repulsão de curto alcance
                # -----------------------------

                minimum_distance = (
                    p1.radius
                    + p2.radius
                )

                repulsion_range = (
                    minimum_distance
                    * REPULSION_RANGE_FACTOR
                )

                if distance < repulsion_range:
                    repulsion_factor = (
                        1.0
                        - distance / repulsion_range
                    )

                    repulsion_force = (
                        REPULSION_STRENGTH
                        * repulsion_factor
                    )

                    total_force -= repulsion_force

                # -----------------------------
                # Aplicar força ao par
                # -----------------------------

                fx = total_force * nx
                fy = total_force * ny

                p1.ax += fx / p1.mass
                p1.ay += fy / p1.mass

                p2.ax -= fx / p2.mass
                p2.ay -= fy / p2.mass

        # =====================================
        # PAREDES
        # =====================================
        #
        # IMPORTANTE:
        # ESTE BLOCO ESTÁ FORA DOS DOIS LOOPS
        # DE PARES DE PARTÍCULAS.
        # =====================================

        if WALLS_ENABLED:
            for particle in self.particles:

                # -----------------------------
                # Parede esquerda
                # -----------------------------

                distance = (
                    particle.x
                    - particle.radius
                )

                if distance < WALL_REPULSION_RANGE:
                    factor = (
                        1.0
                        - distance / WALL_REPULSION_RANGE
                    )

                    force = (
                        WALL_REPULSION_STRENGTH
                        * factor
                    )

                    particle.ax += (
                        force / particle.mass
                    )

                # -----------------------------
                # Parede direita
                # -----------------------------

                distance = (
                    self.width
                    - particle.radius
                    - particle.x
                )

                if distance < WALL_REPULSION_RANGE:
                    factor = (
                        1.0
                        - distance / WALL_REPULSION_RANGE
                    )

                    force = (
                        WALL_REPULSION_STRENGTH
                        * factor
                    )

                    particle.ax -= (
                        force / particle.mass
                    )

                # -----------------------------
                # Parede inferior
                # -----------------------------

                distance = (
                    particle.y
                    - particle.radius
                )

                if distance < WALL_REPULSION_RANGE:
                    factor = (
                        1.0
                        - distance / WALL_REPULSION_RANGE
                    )

                    force = (
                        WALL_REPULSION_STRENGTH
                        * factor
                    )

                    particle.ay += (
                        force / particle.mass
                    )

                # -----------------------------
                # Parede superior
                # -----------------------------

                distance = (
                    self.height
                    - particle.radius
                    - particle.y
                )

                if distance < WALL_REPULSION_RANGE:
                    factor = (
                        1.0
                        - distance / WALL_REPULSION_RANGE
                    )

                    force = (
                        WALL_REPULSION_STRENGTH
                        * factor
                    )

                    particle.ay -= (
                        force / particle.mass
                    )


    def total_potential_energy(self):
        total = 0.0

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

                # ---------------------------------
                # POTENCIAL DA INTERAÇÃO NORMAL
                # ---------------------------------

                if distance < INTERACTION_RANGE:
                    key = tuple(sorted((p1.type, p2.type)))
                    affinity = INTERACTIONS.get(key, 0.0)

                    if affinity != 0:
                        interaction_potential = -(
                            affinity
                            * INTERACTION_STRENGTH
                            * (
                                INTERACTION_RANGE / 2
                                - distance
                                + (
                                    distance * distance
                                    / (2 * INTERACTION_RANGE)
                                )
                            )
                        )

                        total += interaction_potential

                # ---------------------------------
                # POTENCIAL DA REPULSÃO
                # ---------------------------------

                minimum_distance = (
                    p1.radius +
                    p2.radius
                )

                repulsion_range = (
                    minimum_distance
                    * REPULSION_RANGE_FACTOR
                )

                if distance < repulsion_range:
                    repulsion_potential = (
                        REPULSION_STRENGTH
                        * (
                            repulsion_range / 2
                            - distance
                            + (
                                distance * distance
                                / (2 * repulsion_range)
                            )
                        )
                    )

                    total += repulsion_potential

        return total


    def total_energy(self):
        return (
            self.total_kinetic_energy()
            + self.total_potential_energy()
            + self.wall_potential_energy()
        )
        

    def handle_wall_collision(self, particle):
        if particle.x - particle.radius < 0:
            particle.x = particle.radius
            particle.vx *= -1

        elif particle.x + particle.radius > self.width:
            particle.x = self.width - particle.radius
            particle.vx *= -1

        if particle.y - particle.radius < 0:
            particle.y = particle.radius
            particle.vy *= -1

        elif particle.y + particle.radius > self.height:
            particle.y = self.height - particle.radius
            particle.vy *= -1


    def wall_potential_energy(self):
        total = 0.0

        if not WALLS_ENABLED:
            return total

        for particle in self.particles:
            distances = [
                particle.x - particle.radius,
                self.width - particle.radius - particle.x,
                particle.y - particle.radius,
                self.height - particle.radius - particle.y,
            ]

            for distance in distances:
                if distance < WALL_REPULSION_RANGE:
                    potential = (
                        WALL_REPULSION_STRENGTH
                        * (
                            WALL_REPULSION_RANGE / 2
                            - distance
                            + (
                                distance * distance
                                / (2 * WALL_REPULSION_RANGE)
                            )
                        )
                    )

                    total += potential

        return total