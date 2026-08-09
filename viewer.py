import pygame

from universe import Universe
from config import (
    WORLD_WIDTH,
    WORLD_HEIGHT,
    PARTICLE_COUNT,
    SEED,
    TIME_STEP,
)


WINDOW_SIZE = 800

COLORS = {
    "A": (80, 180, 255),
    "B": (255, 190, 70),
    "C": (255, 80, 100),
}

BACKGROUND = (15, 15, 20)
BORDER = (180, 180, 180)
TEXT = (230, 230, 230)


def world_to_screen(x, y):
    screen_x = int(x / WORLD_WIDTH * WINDOW_SIZE)

    # Pygame tem Y crescendo para baixo.
    screen_y = int(
        WINDOW_SIZE -
        (y / WORLD_HEIGHT * WINDOW_SIZE)
    )

    return screen_x, screen_y


def draw_universe(screen, universe, font):
    screen.fill(BACKGROUND)

    pygame.draw.rect(
        screen,
        BORDER,
        (0, 0, WINDOW_SIZE, WINDOW_SIZE),
        2,
    )

    scale = WINDOW_SIZE / WORLD_WIDTH

    for particle in universe.particles:
        x, y = world_to_screen(
            particle.x,
            particle.y,
        )

        radius = max(
            2,
            int(particle.radius * scale)
        )

        color = COLORS.get(
            particle.type,
            (255, 255, 255)
        )

        pygame.draw.circle(
            screen,
            color,
            (x, y),
            radius,
        )

    info = (
        f"Tick: {universe.time}  "
        f"Sim time: {universe.time * TIME_STEP:.2f}  "
        f"Particles: {len(universe.particles)}  "
        f"Collisions: {universe.collision_count}"
    )

    text_surface = font.render(
        info,
        True,
        TEXT
    )

    screen.blit(
        text_surface,
        (10, 10)
    )


def main():
    pygame.init()

    screen = pygame.display.set_mode(
        (WINDOW_SIZE, WINDOW_SIZE)
    )

    pygame.display.set_caption(
        "QMVD Engine - Universe Viewer"
    )

    clock = pygame.time.Clock()

    font = pygame.font.SysFont(
        "monospace",
        16
    )

    universe = Universe(
        width=WORLD_WIDTH,
        height=WORLD_HEIGHT,
        particle_count=PARTICLE_COUNT,
        seed=SEED,
    )

    running = True
    paused = False

    ticks_per_frame = 1

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_SPACE:
                    paused = not paused

                elif event.key == pygame.K_UP:
                    ticks_per_frame *= 2

                elif event.key == pygame.K_DOWN:
                    ticks_per_frame = max(
                        1,
                        ticks_per_frame // 2
                    )

                elif event.key == pygame.K_r:
                    universe = Universe(
                        width=WORLD_WIDTH,
                        height=WORLD_HEIGHT,
                        particle_count=PARTICLE_COUNT,
                        seed=SEED,
                    )

        if not paused:
            for _ in range(ticks_per_frame):
                universe.tick()

        draw_universe(
            screen,
            universe,
            font
        )

        pygame.display.flip()

        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()