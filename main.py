import os
import readline

from universe import Universe
from config import (
    WORLD_WIDTH,
    WORLD_HEIGHT,
    PARTICLE_COUNT,
    SEED,
)


HISTORY_FILE = os.path.expanduser("~/.qmvd_history")


def setup_history():
    if os.path.exists(HISTORY_FILE):
        try:
            readline.read_history_file(HISTORY_FILE)
        except OSError:
            pass

    readline.set_history_length(1000)


def save_history():
    try:
        readline.write_history_file(HISTORY_FILE)
    except OSError:
        pass


def show_help():
    print()
    print("Comandos:")
    print("  status")
    print("  list")
    print("  inspect ID")
    print("  run TICKS")
    print("  clusters")
    print("  cluster-history")
    print("  exit")


def main():
    setup_history()

    universe = Universe(
        width=WORLD_WIDTH,
        height=WORLD_HEIGHT,
        particle_count=PARTICLE_COUNT,
        seed=SEED,
    )

    print()
    print("QMVD ENGINE v2.0")
    print('"Que Merda Vai Dar?"')
    print()
    print("Digite 'help' para ver os comandos.")

    while True:
        try:
            command = input("\nQMVD > ").strip().lower()

        except (EOFError, KeyboardInterrupt):
            print()
            save_history()
            print("Encerrando QMVD Engine.")
            break

        if command == "":
            continue

        elif command == "help":
            show_help()

        elif command == "status":
            universe.status()

        elif command == "list":
            universe.list_particles()

        elif command == "clusters":
            universe.cluster_status()

        elif command == "cluster-history":
            universe.cluster_history_status()

        elif command.startswith("inspect "):
            parts = command.split()

            if len(parts) != 2:
                print("Uso: inspect ID")
                continue

            try:
                particle_id = int(parts[1])

                if particle_id < 0:
                    print("ID inválido.")
                    continue

                universe.inspect(particle_id)

            except ValueError:
                print("ID inválido.")

        elif command.startswith("run "):
            parts = command.split()

            if len(parts) != 2:
                print("Uso: run TICKS")
                continue

            try:
                ticks = int(parts[1])

                if ticks <= 0:
                    print("O número de ticks deve ser maior que zero.")
                    continue

                universe.run(ticks)

                print(
                    f"Universo avançou {ticks} ticks. "
                    f"Tempo atual: {universe.time}"
                )

            except ValueError:
                print("Número de ticks inválido.")

        elif command == "exit":
            save_history()
            print("Encerrando QMVD Engine.")
            break

        else:
            print("Comando desconhecido.")


if __name__ == "__main__":
    main()