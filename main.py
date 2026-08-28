from src.cycle_detector import (
    calculate_mean_force_curve,
    find_cycle_starts,
    get_last_cycle,
)
from src.excel_reader import load_workbook
from src.exporter import plot_last_cycle
from src.user_input import select_excel_file


def main() -> None:
    """Run the 18653 measurement evaluation."""

    print("=== 18653 Auswertung ===\n")

    # Select input file
    excel_file = select_excel_file()

    # Number of setting cycles is currently not needed.
    # setting_cycles = get_setting_cycles()

    # Load measurement data
    workbook = load_workbook(excel_file)

    print("\nDatei erfolgreich geladen:")
    print(excel_file)

    if not workbook:
        print("\nKeine gültigen Messdaten gefunden.")
        return

    print("\nGefundene Tabellenblätter:")

    for sheet_name, data in workbook.items():

        print(f"\n--- {sheet_name} ---")
        print(f"Messpunkte: {len(data)}")

        # Find all detectable cycle starts
        cycle_starts = find_cycle_starts(data)

        print(
            f"Gefundene Zyklusstarts: {cycle_starts}"
        )

        if not cycle_starts:
            print("Kein Zyklus gefunden.")
            continue

        # Get only the LAST cycle
        last_cycle = get_last_cycle(data)

        print(
            f"Messpunkte letzter Zyklus: "
            f"{len(last_cycle)}"
        )

        # Calculate mean force curve
        mean_curve = calculate_mean_force_curve(
            last_cycle
        )

        print(
            f"Höhenbereich der Mittelwertkurve: "
            f"{mean_curve['distance'].min():.4f} "
            f"bis "
            f"{mean_curve['distance'].max():.4f}"
        )

        print("\nErste 5 Werte der Mittelwertkurve:")
        print(mean_curve.head())

        # Plot
        plot_last_cycle(
            sheet_name,
            last_cycle,
            mean_curve,
        )


if __name__ == "__main__":
    main()
