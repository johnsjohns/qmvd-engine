# QMVD Engine configuration

WORLD_WIDTH = 100
WORLD_HEIGHT = 100

PARTICLE_COUNT = 100

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

TIME_STEP = 0.05