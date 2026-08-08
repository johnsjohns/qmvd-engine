from universe import Universe


def main():
    universe = Universe(
        width=100,
        height=100,
        particle_count=10,
        seed=666
    )

    print()
    print("QMCD ENGINE v0.1")
    print('"Que Merda Vai Dar?"')
    print()
    print("Digite 'help' para ver os comandos.")

    while True:
        command = input("\nQMCD > ").strip().lower()

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
            print("Encerrando QMCD Engine.")
            break

        elif command == "":
            continue

        else:
            print("Comando desconhecido.")


if __name__ == "__main__":
    main()