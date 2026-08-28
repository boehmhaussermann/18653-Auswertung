import pandas as pd

from src.cycle_detector import (
    calculate_l1_l2,
    calculate_mean_force_curve,
    find_cycle_starts,
    get_last_cycle,
    print_values_around,
)


from src.excel_reader import load_workbook

from src.user_input import (
    select_excel_file,
    select_export_folder,
)

from src.exporter import (
    plot_last_cycle,
)




def main() -> None:
    """Run the 18653 measurement evaluation."""

    print("=== 18653 Auswertung ===\n")

    # Select input and export file
    excel_file = select_excel_file()

    export_folder = select_export_folder()


    print(
        f"\nExportordner: {export_folder}"
    )


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

    results = []

    for sheet_name, data in workbook.items():

        print(f"\n--- {sheet_name} ---")
        print(f"Messpunkte: {len(data)}")

        cycle_starts = find_cycle_starts(data)

        print(
            f"Gefundene Zyklusstarts: {cycle_starts}"
        )

        if not cycle_starts:
            print("Kein Zyklus gefunden.")
            continue

        last_cycle = get_last_cycle(data)

        print(
            f"Messpunkte letzter Zyklus: "
            f"{len(last_cycle)}"
        )

        mean_curve = calculate_mean_force_curve(
            last_cycle
        )

        # DEBUG
        """ plot_l1_debug(
            mean_curve,
            target_force=350.0,
            height_window=0.05,
        ) """

        # Calculate L1, F1, L2 and F2
        try:

            L1, F1, L2, F2 = calculate_l1_l2(
                mean_curve
            )

            results.append(
                {
                    "Sheet": sheet_name,
                    "L1": L1,
                    "F1": F1,
                    "L2": L2,
                    "F2": F2,
                }
            )

        except ValueError as error:

            print(
                f"\nBerechnung L1/L2 nicht möglich: {error}"
            )

            results.append(
                {
                    "Sheet": sheet_name,
                    "L1": None,
                    "F1": None,
                    "L2": None,
                    "F2": None,
                }
            )

        # Save plot regardless of whether L1/L2 was found
        last_cycle = get_last_cycle(data)
        plot_last_cycle(
            sheet_name,
            last_cycle,
            mean_curve,
            export_folder,
        )


            



    # ============================================================
    # Result summary
    # ============================================================

        if results:

            results_df = pd.DataFrame(results)

            print("\n\n==============================================")
            print("ERGEBNISÜBERSICHT")
            print("==============================================")

            print(
                results_df.to_string(
                    index=False,
                    formatters={
                        "L1": lambda x: "-" if pd.isna(x) else f"{x:.6f}",
                        "F1": lambda x: "-" if pd.isna(x) else f"{x:.3f}",
                        "L2": lambda x: "-" if pd.isna(x) else f"{x:.6f}",
                        "F2": lambda x: "-" if pd.isna(x) else f"{x:.3f}",
                    },
                )
            )
            results_csv = (
                export_folder / "Ergebnisübersicht.csv"
            )

            results_df.to_csv(
                results_csv,
                index=False,
                sep=";",
                decimal=",",
            )

            print(
                f"CSV gespeichert: {results_csv}"
            )





if __name__ == "__main__":
    main()
