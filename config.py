# QMVD Engine configuration

WORLD_WIDTH = 100
WORLD_HEIGHT = 100

PARTICLE_COUNT = 50

SEED = 666

PARTICLE_TYPES = {
    "A": {
        "mass": 1.0,
        "radius": 1.0,
        "weight": 0.50,
    },
    "B": {
        "mass": 2.0,
        "radius": 1.3,
        "weight": 0.30,
    },
    "C": {
        "mass": 4.0,
        "radius": 1.7,
        "weight": 0.20,
    },
}

INTERACTION_RANGE = 10.0
INTERACTION_STRENGTH = 0.002

INTERACTIONS = {
    ("A", "A"): -0.10,
    ("A", "B"):  0.30,
    ("A", "C"): -0.20,
    ("B", "B"):  0.10,
    ("B", "C"):  0.50,
    ("C", "C"): -0.30,
}   

TIME_STEP = 0.025
HARD_COLLISIONS_ENABLED = False
REPULSION_RANGE_FACTOR = 1.2
REPULSION_STRENGTH = 0.0
WALLS_ENABLED = True
WALL_REPULSION_RANGE = 3.0
WALL_REPULSION_STRENGTH = 0.20
CLUSTER_DISTANCE = 4.0
CLUSTER_CHECK_INTERVAL = 10
CLUSTER_TRANSIENT_MAX = 100
CLUSTER_STABLE_MIN = 500
CLUSTER_LONG_LIVED_MIN = 2000