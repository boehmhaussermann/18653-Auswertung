from pathlib import Path

from tkinter import Tk
from tkinter.filedialog import askopenfilename


def select_excel_file() -> Path:
    """Open a file dialog and let the user select an Excel file."""

    root = Tk()
    root.withdraw()

    file_path = askopenfilename(
        title="Messdatei auswählen",
        filetypes=[
            ("Excel-Dateien", "*.xlsx"),
        ],
    )

    root.destroy()

    if not file_path:
        raise SystemExit("Keine Datei ausgewählt.")

    return Path(file_path)


def get_setting_cycles() -> int:
    """Ask the user how many setting cycles were performed."""

    while True:
        try:
            cycles = int(
                input("Wie häufig wurde gesetzt? ")
            )

            if cycles < 0:
                print(
                    "Bitte eine positive ganze Zahl eingeben."
                )
                continue

            return cycles

        except ValueError:
            print("Bitte nur ganze Zahlen eingeben.")