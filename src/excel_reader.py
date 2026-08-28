from pathlib import Path

import pandas as pd


def load_workbook(file_path: Path) -> dict[str, pd.DataFrame]:
    """
    Load all worksheets from an Excel file.

    Expected measurement format:
    - Rows 1–3: metadata
    - Row 4 onward: measurement data
    - Column 1: distance
    - Column 2: load

    Returns:
        Dictionary mapping sheet names to cleaned measurement DataFrames.
    """

    workbook = pd.read_excel(
        file_path,
        sheet_name=None,
        header=None,
    )

    result: dict[str, pd.DataFrame] = {}

    for sheet_name, sheet in workbook.items():

        # Measurement data starts at Excel row 4
        data = sheet.iloc[3:, :2].copy()

        if data.shape[1] < 2:
            print(f"Überspringe Blatt: {sheet_name}")
            continue

        data.columns = ["distance", "load"]

        # Convert decimal commas to decimal points
        data["distance"] = pd.to_numeric(
            data["distance"]
            .astype(str)
            .str.replace(",", ".", regex=False),
            errors="coerce",
        )

        data["load"] = pd.to_numeric(
            data["load"]
            .astype(str)
            .str.replace(",", ".", regex=False),
            errors="coerce",
        )

        # Remove invalid measurements
        data = data.dropna(
            subset=["distance", "load"]
        )

        # Ignore non-measurement worksheets
        if len(data) < 100:
            print(f"Überspringe Blatt: {sheet_name}")
            continue

        result[sheet_name] = data.reset_index(drop=True)

    return result