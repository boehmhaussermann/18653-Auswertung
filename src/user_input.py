from pathlib import Path
from tkinter import Tk
from tkinter.filedialog import askdirectory, askopenfilename


def select_excel_file() -> Path:
    """Open a file dialog and let the user choose an Excel file."""

    root = Tk()
    root.withdraw()

    file_path = askopenfilename(
        title="Messdatei auswählen",
        filetypes=[("Excel-Dateien", "*.xlsx")]
    )

    root.destroy()

    if not file_path:
        raise SystemExit("Keine Datei ausgewählt.")

    return Path(file_path)


def select_export_folder() -> Path:
    """Ask the user where plots and results should be saved."""

    root = Tk()
    root.withdraw()

    folder_path = askdirectory(
        title="Wohin sollen die Diagramme und Ergebnisse gespeichert werden?"
    )

    root.destroy()

    if not folder_path:
        raise SystemExit("Kein Exportordner ausgewählt.")

    return Path(folder_path)
