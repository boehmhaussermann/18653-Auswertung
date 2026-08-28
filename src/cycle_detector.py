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


def calculate_l1_l2(
    mean_curve: pd.DataFrame,
    target_force: float = 350.0,
    height_difference: float = 5.59,
) -> tuple[float, float, float, float]:
    """
    Find the highest height L1 where mean force equals target_force.

    Then calculate:

        L2 = L1 - height_difference

    and interpolate the mean force at L2.

    Returns:
        L1, F1, L2, F2
    """

    curve = mean_curve[
        ["distance", "mean_force"]
    ].dropna().copy()

    curve = curve.sort_values("distance").reset_index(drop=True)

    distance = curve["distance"].to_numpy(dtype=float)
    force = curve["mean_force"].to_numpy(dtype=float)

    print("\n--- Suche L1 ---")
    print(f"Gesuchter F1: {target_force:.3f} N")

    # ---------------------------------------------------------
    # Find EVERY crossing of target_force
    # ---------------------------------------------------------

    l1_candidates = []

    for i in range(len(curve) - 1):

        x1 = distance[i]
        x2 = distance[i + 1]

        y1 = force[i]
        y2 = force[i + 1]

        # Check whether target_force lies between y1 and y2.
        if min(y1, y2) <= target_force <= max(y1, y2):

            # Avoid division by zero for a horizontal segment.
            if y1 == y2:
                l1_candidate = (x1 + x2) / 2.0

            else:
                # Linear interpolation
                l1_candidate = (
                    x1
                    + (target_force - y1)
                    * (x2 - x1)
                    / (y2 - y1)
                )

            l1_candidates.append(l1_candidate)

    # ---------------------------------------------------------
    # Diagnostic information
    # ---------------------------------------------------------

    print(
        f"Kraftbereich: "
        f"{force.min():.3f} N bis "
        f"{force.max():.3f} N"
    )

    if not l1_candidates:
        # This should now be extremely unlikely.
        # Find the closest point for diagnostics.

        closest_index = np.argmin(
            np.abs(force - target_force)
        )

        print(
            "Kein Schnittpunkt gefunden."
        )

        print(
            "Nächster Messpunkt:"
        )

        print(
            f"  L = {distance[closest_index]:.9f}"
        )

        print(
            f"  F = {force[closest_index]:.9f} N"
        )

        raise ValueError(
            f"Kein Schnittpunkt mit "
            f"{target_force} N gefunden."
        )

    # Remove practically identical solutions
    l1_candidates = sorted(l1_candidates)

    unique_candidates = []

    for candidate in l1_candidates:

        if not unique_candidates:
            unique_candidates.append(candidate)

        elif abs(
            candidate - unique_candidates[-1]
        ) > 1e-10:
            unique_candidates.append(candidate)

    print(
        f"Gefundene Schnittpunkte: "
        f"{len(unique_candidates)}"
    )

    print(
        "L1-Kandidaten:"
    )

    for candidate in unique_candidates:
        print(
            f"  L = {candidate:.9f}"
        )

    # ---------------------------------------------------------
    # IMPORTANT:
    #
    # L1 is the HIGHEST height where F = 350 N
    # ---------------------------------------------------------

    L1 = max(unique_candidates)

    F1 = target_force

    # ---------------------------------------------------------
    # Calculate L2
    # ---------------------------------------------------------

    L2 = L1 - height_difference

    # ---------------------------------------------------------
    # Calculate F2 at L2
    # ---------------------------------------------------------

    if L2 < distance.min() or L2 > distance.max():

        raise ValueError(
            f"L2 = {L2:.9f} liegt außerhalb des "
            f"Messbereichs "
            f"({distance.min():.9f} bis "
            f"{distance.max():.9f})."
        )

    F2 = np.interp(
        L2,
        distance,
        force,
    )

    return L1, F1, L2, F2




def print_values_around(
    mean_curve: pd.DataFrame,
    height: float,
    label: str,
    points: int = 3,
) -> None:
    """Print mean-curve values around a specific height."""

    distances = mean_curve["distance"].to_numpy()

    closest_index = np.argmin(
        np.abs(distances - height)
    )

    start = max(0, closest_index - points)
    end = min(
        len(mean_curve),
        closest_index + points + 1,
    )

    print(f"\n--- Werte um {label} = {height:.6f} ---")

    print(
        mean_curve.iloc[start:end][
            [
                "distance",
                "mean_force",
            ]
        ].to_string(index=False)
    )

def calculate_force_range(
    data: pd.DataFrame,
    L1: float,
    L2: float,
) -> tuple[float, float, float]:
    """
    Find Fmax, Fmin and the force difference between L2 and L1.

    Uses the raw measurement data from the last cycle.

    Returns:
        Fmax, Fmin, tolerance
    """

    lower = min(L1, L2)
    upper = max(L1, L2)

    section = data[
        (data["distance"] >= lower)
        & (data["distance"] <= upper)
    ]

    if section.empty:
        raise ValueError(
            f"Keine Messwerte zwischen "
            f"L2={L2:.6f} und L1={L1:.6f} gefunden."
        )

    Fmax = section["load"].max()
    Fmin = section["load"].min()

    tolerance = Fmax - Fmin

    return Fmax, Fmin, tolerance
