import os
import readline
from universe import Universe
from config import (
    WORLD_WIDTH,
    WORLD_HEIGHT,
    PARTICLE_COUNT,
    SEED
)

HISTORY_FILE = os.path.expanduser("~/.qmvd_history")

if os.path.exists(HISTORY_FILE):
    readline.read_history_file(HISTORY_FILE)

readline.set_history_length(1000)

def main():
    universe = Universe(
        width=WORLD_WIDTH,
        height=WORLD_HEIGHT,
        particle_count=PARTICLE_COUNT,
        seed=SEED
    )

    print()
    print("QMVD ENGINE v0.1")
    print('"Que Merda Vai Dar?"')
    print()
    print("Digite 'help' para ver os comandos.")

    while True:
        command = input("\nQMVD > ").strip().lower()

        if command == "help":
            print()
            print("Comandos:")
            print("  status")
            print("  list")
            print("  inspect ID")
            print("  run TICKS")
            print("  exit")

        elif command == "status":
            universe.status()

        elif command == "list":
            universe.list_particles()

        elif command.startswith("inspect "):
            parts = command.split()

            if len(parts) == 2:
                try:
                    particle_id = int(parts[1])
                    universe.inspect(particle_id)

                except ValueError:
                    print("ID inválido.")

        elif command.startswith("run "):
            parts = command.split()

            if len(parts) == 2:
                try:
                    ticks = int(parts[1])

                    universe.run(ticks)

                    print(
                        f"Universo avançou {ticks} ticks. "
                        f"Tempo atual: {universe.time}"
                    )

                except ValueError:
                    print("Número de ticks inválido.")

        elif command == "exit":
            readline.write_history_file(HISTORY_FILE)
            print("Encerrando QMVD Engine.")
            break

        elif command == "":
            continue

        else:
            print("Comando desconhecido.")


if __name__ == "__main__":
    main()