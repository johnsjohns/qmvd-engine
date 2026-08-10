import math


def distance(p1, p2):
    dx = p2.x - p1.x
    dy = p2.y - p1.y

    return math.sqrt(
        dx * dx +
        dy * dy
    )


def find_clusters(particles, max_distance):
    visited = set()
    clusters = []

    for particle in particles:
        if particle.id in visited:
            continue

        cluster = []
        stack = [particle]

        while stack:
            current = stack.pop()

            if current.id in visited:
                continue

            visited.add(current.id)
            cluster.append(current)

            for other in particles:
                if other.id in visited:
                    continue

                if current.id == other.id:
                    continue

                if distance(current, other) <= max_distance:
                    stack.append(other)

        clusters.append(cluster)

    return clusters