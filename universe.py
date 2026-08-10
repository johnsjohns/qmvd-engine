import math
import random

from tqdm import tqdm

from particle import Particle
from cluster import find_clusters

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
    CLUSTER_DISTANCE,
    CLUSTER_CHECK_INTERVAL,
    CLUSTER_TRANSIENT_MAX,
    CLUSTER_STABLE_MIN,
    CLUSTER_LONG_LIVED_MIN,
)


class Universe:
    def __init__(
        self,
        width=100,
        height=100,
        particle_count=10,
        seed=666,
    ):
        self.width = width
        self.height = height
        self.seed = seed

        self.time = 0
        self.collision_count = 0

        random.seed(seed)

        self.particles = []

        # =====================================
        # CRIAÇÃO DAS PARTÍCULAS
        # =====================================

        type_names = list(PARTICLE_TYPES.keys())

        type_weights = [
            PARTICLE_TYPES[name]["weight"]
            for name in type_names
        ]

        for particle_id in range(particle_count):
            particle_type = random.choices(
                type_names,
                weights=type_weights,
                k=1,
            )[0]

            properties = PARTICLE_TYPES[
                particle_type
            ]

            particle = Particle(
                particle_id,
                self.width,
                self.height,
                particle_type,
                properties["mass"],
                properties["radius"],
            )

            self.particles.append(particle)

        # =====================================
        # ENERGIA INICIAL
        # =====================================

        self.initial_total_energy = (
            self.total_energy()
        )

        self.initial_kinetic_energy = (
            self.total_kinetic_energy()
        )

        # =====================================
        # HISTÓRICO DE CLUSTERS
        # =====================================

        self.cluster_history = {}

    # =========================================
    # SIMULAÇÃO
    # =========================================

    def tick(self):
        dt = TIME_STEP

        # 1. Acelerações no início do passo
        self.calculate_accelerations()

        # 2. Atualizar posição e metade da velocidade
        for particle in self.particles:
            particle.x += (
                particle.vx * dt
                + 0.5
                * particle.ax
                * dt
                * dt
            )

            particle.y += (
                particle.vy * dt
                + 0.5
                * particle.ay
                * dt
                * dt
            )

            particle.vx += (
                0.5
                * particle.ax
                * dt
            )

            particle.vy += (
                0.5
                * particle.ay
                * dt
            )

        # 3. Colisões rígidas opcionais
        if HARD_COLLISIONS_ENABLED:
            self.handle_collisions()

        # 4. Recalcular acelerações
        self.calculate_accelerations()

        # 5. Completar atualização da velocidade
        for particle in self.particles:
            particle.vx += (
                0.5
                * particle.ax
                * dt
            )

            particle.vy += (
                0.5
                * particle.ay
                * dt
            )

        # 6. Avançar relógio
        self.time += 1

        # 7. Observar clusters periodicamente
        if (
            self.time
            % CLUSTER_CHECK_INTERVAL
            == 0
        ):
            self.update_cluster_history()

    def run(self, ticks):
        for _ in tqdm(
            range(ticks),
            desc="Simulando",
            unit="tick",
            dynamic_ncols=True,
        ):
            self.tick()

    # =========================================
    # FORÇAS E ACELERAÇÕES
    # =========================================

    def calculate_accelerations(self):
        # Zerar acelerações
        for particle in self.particles:
            particle.ax = 0.0
            particle.ay = 0.0

        particle_count = len(
            self.particles
        )

        # =====================================
        # INTERAÇÕES PARTÍCULA-PARTÍCULA
        # =====================================

        for i in range(particle_count):
            for j in range(
                i + 1,
                particle_count,
            ):
                p1 = self.particles[i]
                p2 = self.particles[j]

                dx = p2.x - p1.x
                dy = p2.y - p1.y

                distance_squared = (
                    dx * dx
                    + dy * dy
                )

                if distance_squared == 0:
                    continue

                distance = math.sqrt(
                    distance_squared
                )

                nx = dx / distance
                ny = dy / distance

                total_force = 0.0

                # ---------------------------------
                # AFINIDADE ENTRE TIPOS
                # ---------------------------------

                if (
                    distance
                    < INTERACTION_RANGE
                ):
                    key = tuple(
                        sorted(
                            (
                                p1.type,
                                p2.type,
                            )
                        )
                    )

                    affinity = (
                        INTERACTIONS.get(
                            key,
                            0.0,
                        )
                    )

                    if affinity != 0:
                        distance_factor = (
                            1.0
                            - distance
                            / INTERACTION_RANGE
                        )

                        interaction_force = (
                            affinity
                            * INTERACTION_STRENGTH
                            * distance_factor
                        )

                        total_force += (
                            interaction_force
                        )

                # ---------------------------------
                # REPULSÃO DE CURTO ALCANCE
                # ---------------------------------

                minimum_distance = (
                    p1.radius
                    + p2.radius
                )

                repulsion_range = (
                    minimum_distance
                    * REPULSION_RANGE_FACTOR
                )

                if (
                    distance
                    < repulsion_range
                ):
                    repulsion_factor = (
                        1.0
                        - distance
                        / repulsion_range
                    )

                    repulsion_force = (
                        REPULSION_STRENGTH
                        * repulsion_factor
                    )

                    # Negativo = afastar
                    total_force -= (
                        repulsion_force
                    )

                # ---------------------------------
                # APLICAR FORÇA
                # ---------------------------------

                fx = (
                    total_force
                    * nx
                )

                fy = (
                    total_force
                    * ny
                )

                p1.ax += (
                    fx / p1.mass
                )

                p1.ay += (
                    fy / p1.mass
                )

                p2.ax -= (
                    fx / p2.mass
                )

                p2.ay -= (
                    fy / p2.mass
                )

        # =====================================
        # PAREDES POR POTENCIAL
        # =====================================

        if WALLS_ENABLED:
            for particle in self.particles:

                # Parede esquerda
                distance = (
                    particle.x
                    - particle.radius
                )

                if (
                    distance
                    < WALL_REPULSION_RANGE
                ):
                    factor = (
                        1.0
                        - distance
                        / WALL_REPULSION_RANGE
                    )

                    force = (
                        WALL_REPULSION_STRENGTH
                        * factor
                    )

                    particle.ax += (
                        force
                        / particle.mass
                    )

                # Parede direita
                distance = (
                    self.width
                    - particle.radius
                    - particle.x
                )

                if (
                    distance
                    < WALL_REPULSION_RANGE
                ):
                    factor = (
                        1.0
                        - distance
                        / WALL_REPULSION_RANGE
                    )

                    force = (
                        WALL_REPULSION_STRENGTH
                        * factor
                    )

                    particle.ax -= (
                        force
                        / particle.mass
                    )

                # Parede inferior
                distance = (
                    particle.y
                    - particle.radius
                )

                if (
                    distance
                    < WALL_REPULSION_RANGE
                ):
                    factor = (
                        1.0
                        - distance
                        / WALL_REPULSION_RANGE
                    )

                    force = (
                        WALL_REPULSION_STRENGTH
                        * factor
                    )

                    particle.ay += (
                        force
                        / particle.mass
                    )

                # Parede superior
                distance = (
                    self.height
                    - particle.radius
                    - particle.y
                )

                if (
                    distance
                    < WALL_REPULSION_RANGE
                ):
                    factor = (
                        1.0
                        - distance
                        / WALL_REPULSION_RANGE
                    )

                    force = (
                        WALL_REPULSION_STRENGTH
                        * factor
                    )

                    particle.ay -= (
                        force
                        / particle.mass
                    )

    # =========================================
    # COLISÕES RÍGIDAS OPCIONAIS
    # =========================================

    def handle_collisions(self):
        particle_count = len(
            self.particles
        )

        for i in range(particle_count):
            for j in range(
                i + 1,
                particle_count,
            ):
                p1 = self.particles[i]
                p2 = self.particles[j]

                dx = p2.x - p1.x
                dy = p2.y - p1.y

                distance_squared = (
                    dx * dx
                    + dy * dy
                )

                min_distance = (
                    p1.radius
                    + p2.radius
                )

                if (
                    distance_squared
                    <= min_distance
                    * min_distance
                ):
                    self.resolve_collision(
                        p1,
                        p2,
                    )

    def resolve_collision(
        self,
        p1,
        p2,
    ):
        dx = p2.x - p1.x
        dy = p2.y - p1.y

        distance = math.sqrt(
            dx * dx
            + dy * dy
        )

        if distance == 0:
            dx = 0.01
            dy = 0.0
            distance = 0.01

        nx = dx / distance
        ny = dy / distance

        relative_vx = (
            p2.vx - p1.vx
        )

        relative_vy = (
            p2.vy - p1.vy
        )

        velocity_along_normal = (
            relative_vx * nx
            + relative_vy * ny
        )

        if velocity_along_normal > 0:
            self.correct_overlap(
                p1,
                p2,
                nx,
                ny,
                distance,
            )
            return

        restitution = 1.0

        impulse = -(
            (1 + restitution)
            * velocity_along_normal
        )

        impulse /= (
            (1 / p1.mass)
            + (1 / p2.mass)
        )

        impulse_x = (
            impulse * nx
        )

        impulse_y = (
            impulse * ny
        )

        p1.vx -= (
            impulse_x
            / p1.mass
        )

        p1.vy -= (
            impulse_y
            / p1.mass
        )

        p2.vx += (
            impulse_x
            / p2.mass
        )

        p2.vy += (
            impulse_y
            / p2.mass
        )

        self.correct_overlap(
            p1,
            p2,
            nx,
            ny,
            distance,
        )

        self.collision_count += 1

    def correct_overlap(
        self,
        p1,
        p2,
        nx,
        ny,
        distance,
    ):
        min_distance = (
            p1.radius
            + p2.radius
        )

        overlap = (
            min_distance
            - distance
        )

        if overlap <= 0:
            return

        inverse_mass_1 = (
            1.0 / p1.mass
        )

        inverse_mass_2 = (
            1.0 / p2.mass
        )

        inverse_mass_sum = (
            inverse_mass_1
            + inverse_mass_2
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

        p1.x -= (
            nx * correction_1
        )

        p1.y -= (
            ny * correction_1
        )

        p2.x += (
            nx * correction_2
        )

        p2.y += (
            ny * correction_2
        )

    # =========================================
    # ENERGIA
    # =========================================

    def total_kinetic_energy(self):
        total = 0.0

        for particle in self.particles:
            speed_squared = (
                particle.vx
                * particle.vx
                + particle.vy
                * particle.vy
            )

            total += (
                0.5
                * particle.mass
                * speed_squared
            )

        return total

    def total_potential_energy(self):
        total = 0.0

        particle_count = len(
            self.particles
        )

        for i in range(particle_count):
            for j in range(
                i + 1,
                particle_count,
            ):
                p1 = self.particles[i]
                p2 = self.particles[j]

                dx = p2.x - p1.x
                dy = p2.y - p1.y

                distance_squared = (
                    dx * dx
                    + dy * dy
                )

                if distance_squared == 0:
                    continue

                distance = math.sqrt(
                    distance_squared
                )

                # ---------------------------------
                # POTENCIAL DA AFINIDADE
                # ---------------------------------

                if (
                    distance
                    < INTERACTION_RANGE
                ):
                    key = tuple(
                        sorted(
                            (
                                p1.type,
                                p2.type,
                            )
                        )
                    )

                    affinity = (
                        INTERACTIONS.get(
                            key,
                            0.0,
                        )
                    )

                    if affinity != 0:
                        interaction_potential = -(
                            affinity
                            * INTERACTION_STRENGTH
                            * (
                                INTERACTION_RANGE
                                / 2
                                - distance
                                + (
                                    distance
                                    * distance
                                    / (
                                        2
                                        * INTERACTION_RANGE
                                    )
                                )
                            )
                        )

                        total += (
                            interaction_potential
                        )

                # ---------------------------------
                # POTENCIAL DA REPULSÃO CURTA
                # ---------------------------------

                minimum_distance = (
                    p1.radius
                    + p2.radius
                )

                repulsion_range = (
                    minimum_distance
                    * REPULSION_RANGE_FACTOR
                )

                if (
                    distance
                    < repulsion_range
                ):
                    repulsion_potential = (
                        REPULSION_STRENGTH
                        * (
                            repulsion_range
                            / 2
                            - distance
                            + (
                                distance
                                * distance
                                / (
                                    2
                                    * repulsion_range
                                )
                            )
                        )
                    )

                    total += (
                        repulsion_potential
                    )

        return total

    def wall_potential_energy(self):
        total = 0.0

        if not WALLS_ENABLED:
            return total

        for particle in self.particles:
            distances = [
                (
                    particle.x
                    - particle.radius
                ),
                (
                    self.width
                    - particle.radius
                    - particle.x
                ),
                (
                    particle.y
                    - particle.radius
                ),
                (
                    self.height
                    - particle.radius
                    - particle.y
                ),
            ]

            for distance in distances:
                if (
                    distance
                    < WALL_REPULSION_RANGE
                ):
                    potential = (
                        WALL_REPULSION_STRENGTH
                        * (
                            WALL_REPULSION_RANGE
                            / 2
                            - distance
                            + (
                                distance
                                * distance
                                / (
                                    2
                                    * WALL_REPULSION_RANGE
                                )
                            )
                        )
                    )

                    total += potential

        return total

    def total_energy(self):
        return (
            self.total_kinetic_energy()
            + self.total_potential_energy()
            + self.wall_potential_energy()
        )

    # =========================================
    # MOMENTO
    # =========================================

    def total_momentum(self):
        px = 0.0
        py = 0.0

        for particle in self.particles:
            px += (
                particle.mass
                * particle.vx
            )

            py += (
                particle.mass
                * particle.vy
            )

        return px, py

    # =========================================
    # STATUS
    # =========================================

    def particle_type_counts(self):
        counts = {}

        for particle in self.particles:
            counts[particle.type] = (
                counts.get(
                    particle.type,
                    0,
                )
                + 1
            )

        return counts

    def status(self):
        print()
        print("=== QMVD ENGINE ===")

        print(
            f"Seed: {self.seed}"
        )

        print(
            f"Time: {self.time} ticks"
        )

        print(
            f"Time step: {TIME_STEP}"
        )

        print(
            f"Simulation time: "
            f"{self.time * TIME_STEP:.3f}"
        )

        print(
            f"World: "
            f"{self.width} x {self.height}"
        )

        print(
            f"Particles: "
            f"{len(self.particles)}"
        )

        print(
            f"Collisions: "
            f"{self.collision_count}"
        )

        kinetic_energy = (
            self.total_kinetic_energy()
        )

        particle_potential = (
            self.total_potential_energy()
        )

        wall_potential = (
            self.wall_potential_energy()
        )

        total_energy = (
            kinetic_energy
            + particle_potential
            + wall_potential
        )

        energy_drift = (
            total_energy
            - self.initial_total_energy
        )

        momentum_x, momentum_y = (
            self.total_momentum()
        )

        print()

        print(
            f"Kinetic energy:        "
            f"{kinetic_energy:.9f}"
        )

        print(
            f"Particle potential:    "
            f"{particle_potential:.9f}"
        )

        print(
            f"Wall potential:        "
            f"{wall_potential:.9f}"
        )

        print(
            f"Total energy:          "
            f"{total_energy:.9f}"
        )

        print(
            f"Energy drift:          "
            f"{energy_drift:+.9e}"
        )

        print(
            f"Momentum: "
            f"({momentum_x:.6f}, "
            f"{momentum_y:.6f})"
        )

        counts = (
            self.particle_type_counts()
        )

        print(
            "Types: "
            + ", ".join(
                f"{particle_type}={count}"
                for particle_type, count
                in sorted(
                    counts.items()
                )
            )
        )

        print()

    def list_particles(self):
        for particle in self.particles:
            print(particle)

    def inspect(self, particle_id):
        for particle in self.particles:
            if (
                particle.id
                == particle_id
            ):
                print(particle)
                return

        print(
            "Partícula não encontrada."
        )

    # =========================================
    # CLUSTERS
    # =========================================

    def clusters(self):
        return find_clusters(
            self.particles,
            CLUSTER_DISTANCE,
        )

    def cluster_status(self):
        clusters = self.clusters()

        real_clusters = [
            cluster
            for cluster in clusters
            if len(cluster) > 1
        ]

        print()
        print("=== CLUSTERS ===")

        print(
            f"Detected: "
            f"{len(real_clusters)}"
        )

        for index, cluster in enumerate(
            real_clusters,
            start=1,
        ):
            composition = {}

            for particle in cluster:
                composition[
                    particle.type
                ] = (
                    composition.get(
                        particle.type,
                        0,
                    )
                    + 1
                )

            composition_text = (
                ", ".join(
                    f"{particle_type}={count}"
                    for particle_type, count
                    in sorted(
                        composition.items()
                    )
                )
            )

            ids = ", ".join(
                str(particle.id)
                for particle in cluster
            )

            print(
                f"Cluster #{index} | "
                f"Size={len(cluster)} | "
                f"{composition_text} | "
                f"Particles=[{ids}]"
            )

        print()

    # =========================================
    # HISTÓRICO DOS CLUSTERS
    # =========================================

    def update_cluster_history(self):
        clusters = self.clusters()

        active_keys = set()

        for cluster in clusters:
            if len(cluster) <= 1:
                continue

            key = tuple(
                sorted(
                    particle.id
                    for particle
                    in cluster
                )
            )

            active_keys.add(key)

            if (
                key
                not in self.cluster_history
            ):
                self.cluster_history[key] = {
                    "first_seen": self.time,
                    "last_seen": self.time,
                    "observations": 1,
                    "current_streak": 1,
                    "longest_streak": 1,
                    "appearances": 1,
                    "active": True,
                }

            else:
                data = (
                    self.cluster_history[
                        key
                    ]
                )

                if data["active"]:
                    data[
                        "current_streak"
                    ] += 1

                else:
                    data[
                        "current_streak"
                    ] = 1

                    data[
                        "appearances"
                    ] += 1

                data["active"] = True

                data["last_seen"] = (
                    self.time
                )

                data[
                    "observations"
                ] += 1

                if (
                    data["current_streak"]
                    > data["longest_streak"]
                ):
                    data[
                        "longest_streak"
                    ] = data[
                        "current_streak"
                    ]

        for (
            key,
            data,
        ) in self.cluster_history.items():

            if key not in active_keys:
                data["active"] = False

                data[
                    "current_streak"
                ] = 0

    def cluster_history_status(self):
        if not self.cluster_history:
            print()
            print(
                "Nenhum cluster registrado."
            )
            print()
            return

        print()
        print(
            "=== CLUSTER HISTORY ==="
        )

        records = sorted(
            self.cluster_history.items(),
            key=lambda item: (
                item[1][
                    "longest_streak"
                ]
            ),
            reverse=True,
        )

        for (
            key,
            data,
        ) in records[:20]:

            ids = ", ".join(
                str(particle_id)
                for particle_id
                in key
            )

            # ---------------------------------
            # TEMPO DE VIDA
            # ---------------------------------

            longest_ticks = (
                data["longest_streak"]
                * CLUSTER_CHECK_INTERVAL
            )

            current_ticks = (
                data["current_streak"]
                * CLUSTER_CHECK_INTERVAL
            )

            longest_time = (
                longest_ticks
                * TIME_STEP
            )

            # ---------------------------------
            # CLASSIFICAÇÃO
            # ---------------------------------

            if (
                longest_ticks
                < CLUSTER_TRANSIENT_MAX
            ):
                classification = (
                    "TRANSIENT"
                )

            elif (
                longest_ticks
                < CLUSTER_STABLE_MIN
            ):
                classification = (
                    "TEMPORARY"
                )

            elif (
                longest_ticks
                < CLUSTER_LONG_LIVED_MIN
            ):
                classification = (
                    "STABLE"
                )

            else:
                classification = (
                    "LONG-LIVED"
                )

            # ---------------------------------
            # COMPOSIÇÃO
            # ---------------------------------

            composition = {}

            for particle_id in key:
                particle = next(
                    (
                        p
                        for p in self.particles
                        if p.id
                        == particle_id
                    ),
                    None,
                )

                if particle is not None:
                    composition[
                        particle.type
                    ] = (
                        composition.get(
                            particle.type,
                            0,
                        )
                        + 1
                    )

            composition_text = (
                ", ".join(
                    f"{particle_type}={count}"
                    for particle_type, count
                    in sorted(
                        composition.items()
                    )
                )
            )

            # ---------------------------------
            # ESTADO ATUAL
            # ---------------------------------

            state = (
                "ACTIVE"
                if data["active"]
                else "inactive"
            )

            print(
                f"Particles=[{ids}] | "
                f"Composition={composition_text} | "
                f"Longest={longest_ticks} ticks | "
                f"SimTime={longest_time:.3f} | "
                f"Current={current_ticks} ticks | "
                f"Appearances={data['appearances']} | "
                f"Seen={data['observations']}x | "
                f"{classification} | "
                f"{state}"
            )

        print()