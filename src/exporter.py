import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path


def plot_last_cycle(
    sheet_name: str,
    last_cycle: pd.DataFrame,
    mean_curve: pd.DataFrame,
) -> None:
    """
    Plot the two halves of the last cycle and their mean force curve.
    """

    plt.figure(figsize=(12, 6))

    # Original last cycle
    plt.plot(
        last_cycle["distance"],
        last_cycle["load"],
        color="lightgray",
        linewidth=1,
        label="Last cycle",
    )

    # First half
    plt.plot(
        mean_curve["distance"],
        mean_curve["first_half_force"],
        color="blue",
        linewidth=1.5,
        label="First half",
    )

    # Second half
    plt.plot(
        mean_curve["distance"],
        mean_curve["second_half_force"],
        color="green",
        linewidth=1.5,
        label="Second half",
    )

    # Mean
    plt.plot(
        mean_curve["distance"],
        mean_curve["mean_force"],
        color="red",
        linewidth=2,
        label="Mean force",
    )

    plt.title(f"{sheet_name} – letzter Zyklus")
    plt.xlabel("Distance")
    plt.ylabel("Load")

    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    plt.savefig(...)
    plt.close()

def plot_last_cycle(
    sheet_name: str,
    last_cycle: pd.DataFrame,
    mean_curve: pd.DataFrame,
    output_folder: Path,
) -> None:

    plt.figure(figsize=(12, 6))

    plt.plot(
        last_cycle["distance"],
        last_cycle["load"],
        linewidth=1,
        alpha=0.5,
        label="Messdaten",
    )

    plt.plot(
        mean_curve["distance"],
        mean_curve["mean_force"],
        linewidth=2,
        label="Mittlere Kraft",
    )

    plt.title(sheet_name)
    plt.xlabel("Distance")
    plt.ylabel("Load")

    plt.grid(True)
    plt.legend()

    plt.tight_layout()

    output_file = (
        output_folder
        / f"{sheet_name}_Auswertung.png"
    )

    plt.savefig(
        output_file,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def plot_last_cycle(
    sheet_name: str,
    last_cycle: pd.DataFrame,
    mean_curve: pd.DataFrame,
    output_folder: Path,
) -> None:
    """Save the last cycle and mean force curve as a PNG."""

    plt.figure(figsize=(12, 6))

    # Original measurement data
    plt.plot(
        last_cycle["distance"],
        last_cycle["load"],
        linewidth=1,
        alpha=0.5,
        label="Messdaten",
    )

    # Mean force curve
    plt.plot(
        mean_curve["distance"],
        mean_curve["mean_force"],
        linewidth=2,
        label="Mittlere Kraft",
    )

    plt.title(sheet_name)
    plt.xlabel("Distance")
    plt.ylabel("Load")

    plt.grid(True)
    plt.legend()
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

    print(f"Diagramm gespeichert: {output_file}")
