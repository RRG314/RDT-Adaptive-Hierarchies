"""Known-form geometry validation example."""

from __future__ import annotations

from rdt_adaptive_hierarchy.applications.geometry_validation import run_geometry_validation


def main() -> None:
    rows = run_geometry_validation([1.0])
    for row in rows:
        print({
            "method": row.method,
            "max_relative_error": round(row.max_relative_error, 8),
            "mean_relative_error": round(row.mean_relative_error, 8),
        })


if __name__ == "__main__":
    main()
