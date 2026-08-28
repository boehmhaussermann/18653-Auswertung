import matplotlib.pyplot as plt
import pandas as pd


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

    plt.show()
