import numpy as np
import pandas as pd


def find_cycle_starts(
    data: pd.DataFrame,
    threshold: float = 10.0,
) -> list[int]:
    """
    Find indices where the load crosses the threshold upwards.

    A cycle starts when:
        previous load < threshold
        current load >= threshold
    """

    starts: list[int] = []

    for i in range(1, len(data)):

        previous_force = data["load"].iloc[i - 1]
        current_force = data["load"].iloc[i]

        if (
            previous_force < threshold
            and current_force >= threshold
        ):
            starts.append(i)

    return starts


def get_last_cycle(
    data: pd.DataFrame,
    threshold: float = 10.0,
) -> pd.DataFrame:
    """
    Extract the last cycle from the measurement data.

    The last cycle starts at the last upward crossing of the
    force threshold and continues until the end of the measurement.
    """

    cycle_starts = find_cycle_starts(
        data,
        threshold=threshold,
    )

    if not cycle_starts:
        raise ValueError(
            f"Kein Zyklusstart bei {threshold} N gefunden."
        )

    last_start = cycle_starts[-1]

    last_cycle = data.iloc[last_start:].copy()

    return last_cycle.reset_index(drop=True)


def _prepare_branch(
    data: pd.DataFrame,
    height_column: str = "distance",
    force_column: str = "load",
) -> pd.DataFrame:
    """
    Prepare one cycle branch for interpolation.

    The height is sorted in ascending order and duplicate heights
    are averaged.
    """

    branch = data[
        [height_column, force_column]
    ].copy()

    branch = branch.dropna()

    # Sort by height
    branch = branch.sort_values(height_column)

    # If several measurements have essentially the same height,
    # use their mean force.
    branch = (
        branch
        .groupby(height_column, as_index=False)[force_column]
        .mean()
    )

    return branch


def calculate_mean_force_curve(
    last_cycle: pd.DataFrame,
    points: int = 500,
) -> pd.DataFrame:
    """
    Calculate the mean force for each height of the last cycle.

    The last cycle is split at its minimum height:

        first half  = cycle start -> minimum height
        second half = minimum height -> cycle end

    Both halves are interpolated onto a common height grid.

    The resulting mean force is:

        mean_force = (first_half_force + second_half_force) / 2

    Returns:
        DataFrame with:
            distance
            first_half_force
            second_half_force
            mean_force
    """

    if len(last_cycle) < 3:
        raise ValueError(
            "Der letzte Zyklus enthält zu wenige Messpunkte."
        )

    # Find the minimum height
    minimum_index = last_cycle["distance"].idxmin()

    # Split at minimum height
    first_half = last_cycle.loc[
        :minimum_index
    ].copy()

    second_half = last_cycle.loc[
        minimum_index:
    ].copy()

    if len(first_half) < 2 or len(second_half) < 2:
        raise ValueError(
            "Der letzte Zyklus konnte nicht sinnvoll "
            "in zwei Hälften geteilt werden."
        )

    # First half is normally descending in height.
    # Reverse it so that height increases for interpolation.
    first_half = first_half.iloc[::-1]

    # Prepare both branches
    first_branch = _prepare_branch(first_half)
    second_branch = _prepare_branch(second_half)

    # Determine the height range where BOTH branches have data.
    overlap_min = max(
        first_branch["distance"].min(),
        second_branch["distance"].min(),
    )

    overlap_max = min(
        first_branch["distance"].max(),
        second_branch["distance"].max(),
    )

    if overlap_min >= overlap_max:
        raise ValueError(
            "Die beiden Zyklushälften haben keinen "
            "gemeinsamen Höhenbereich."
        )

    # Common height grid
    common_distance = np.linspace(
        overlap_min,
        overlap_max,
        points,
    )

    # Interpolate both branches
    first_force = np.interp(
        common_distance,
        first_branch["distance"],
        first_branch["load"],
    )

    second_force = np.interp(
        common_distance,
        second_branch["distance"],
        second_branch["load"],
    )

    # Calculate mean force
    mean_force = (
        first_force + second_force
    ) / 2.0

    return pd.DataFrame(
        {
            "distance": common_distance,
            "first_half_force": first_force,
            "second_half_force": second_force,
            "mean_force": mean_force,
        }
    )
