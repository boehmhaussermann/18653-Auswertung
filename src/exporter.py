from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

def plot_last_cycle(
    sheet_name: str,
    last_cycle: pd.DataFrame,
    mean_curve: pd.DataFrame,
    output_folder: Path,
) -> None:
    """Save the last cycle and mean force curves as a PNG."""

    plt.figure(figsize=(12, 6))

    # Original last cycle
    """ plt.plot(
        last_cycle["distance"],
        last_cycle["load"],
        color="#7A8793",
        linewidth=0.75,
        alpha=0.65,
        label="Messdaten",
    ) """

    # First half
    plt.plot(
        mean_curve["distance"],
        mean_curve["first_half_force"],
        color="#2F5597",
        linewidth=1.25,
        label="Loading",
    )

    # Second half
    plt.plot(
        mean_curve["distance"],
        mean_curve["second_half_force"],
        color="#548235",
        linewidth=1.00,
        label="Unloading",
    )

    # Mean force
    plt.plot(
        mean_curve["distance"],
        mean_curve["mean_force"],
        color="#005B96",
        linewidth=1.50,
        label="Mean Force",
    )

    plt.title(
        f"{sheet_name}",
        fontsize=14,
        fontweight="bold",
    )

    plt.xlabel(
        "Distance [mm]",
        fontsize=11,
    )

    plt.ylabel(
        "Force [N]",
        fontsize=11,
    )

    plt.grid(
        True,
        color="#D9DEE3",
        linewidth=0.7,
        alpha=0.8,
    )

    plt.legend(
        frameon=False,
    )

    plt.tight_layout()

    output_file = (
        output_folder / f"{sheet_name}_Auswertung.png"
    )

    plt.savefig(
        output_file,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()

    print(
        f"Diagramm gespeichert: {output_file}"
    )
