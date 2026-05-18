"""Small memory-reporting helpers for benchmark runs."""

from __future__ import annotations

import os
import resource


def process_rss_kib() -> float:
    """Return current process resident set size in KiB when available."""

    try:
        import psutil  # type: ignore

        return float(psutil.Process(os.getpid()).memory_info().rss / 1024.0)
    except Exception:
        usage = resource.getrusage(resource.RUSAGE_SELF)
        # macOS reports bytes, Linux reports KiB. Values under one TiB are
        # treated as bytes on macOS and normalized to KiB.
        value = float(usage.ru_maxrss)
        return value / 1024.0 if value > 10_000_000 else value
