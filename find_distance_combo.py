import argparse
import json
from itertools import product
from math import isclose


def float_range(start, stop, step):
    while start <= stop + 1e-9:
        yield round(start, 6)
        start += step


def find_best_combination(
    distances, from_gap, to_gap, total_length, tolerance=1e-3, gap_step=0.1
):
    best_result = None

    for gap in float_range(from_gap, to_gap, gap_step):
        max_counts = int(total_length // min(distances)) + 1

        for base_count in range(1, max_counts + 1):
            base_combos = product([base_count - 1, base_count], repeat=len(distances))

            for counts in base_combos:
                if sum(counts) == 0:
                    continue
                num_gaps = sum(counts) - 1
                total_gaps = num_gaps * gap
                total_distance = sum(d * c for d, c in zip(distances, counts))
                total_combined = total_distance + total_gaps

                if isclose(total_combined, total_length, abs_tol=tolerance):
                    nonzero_counts = [c for c in counts if c > 0]
                    imbalance = max(nonzero_counts) - min(nonzero_counts)
                    used_dist_count = sum(1 for c in counts if c > 0)
                    if (
                        best_result is None
                        or used_dist_count > best_result["used_count"]
                        or (
                            used_dist_count == best_result["used_count"]
                            and imbalance < best_result["imbalance"]
                        )
                    ):
                        best_result = {
                            "gap": round(gap, 4),
                            "total_length": round(total_combined, 4),
                            "counts": {
                                round(d, 4): c
                                for d, c in zip(distances, counts)
                                if c > 0
                            },
                            "imbalance": imbalance,
                            "used_count": used_dist_count,
                        }

    if best_result:
        del best_result["imbalance"]
        del best_result["used_count"]
        return best_result
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Find combination of distances with float gaps."
    )
    parser.add_argument(
        "--distances",
        type=float,
        nargs="+",
        required=True,
        help="List of 1 to 10 float distances (e.g. 25.5 40 80)",
    )
    parser.add_argument(
        "--from_gap", type=float, required=True, help="Minimum gap (float)"
    )
    parser.add_argument(
        "--to_gap", type=float, required=True, help="Maximum gap (float)"
    )
    parser.add_argument(
        "--total_length", type=float, required=True, help="Target total length (float)"
    )
    parser.add_argument(
        "--tolerance",
        type=float,
        default=1e-3,
        help="Length tolerance (default: 0.001)",
    )
    parser.add_argument(
        "--gap_step", type=float, default=0.1, help="Gap increment step (default: 0.1)"
    )

    args = parser.parse_args()

    if not (1 <= len(args.distances) <= 10):
        print("Error: Please provide between 1 and 10 distances.")
        return

    result = find_best_combination(
        args.distances,
        args.from_gap,
        args.to_gap,
        args.total_length,
        args.tolerance,
        args.gap_step,
    )

    if result:
        print(json.dumps(result, indent=2, sort_keys=True))
        print(result)
    else:
        print("No suitable combination found.")


if __name__ == "__main__":
    main()
