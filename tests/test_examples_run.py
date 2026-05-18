import os
import subprocess
import sys
from pathlib import Path


def test_examples_execute_without_failure():
    root = Path(__file__).resolve().parents[1]
    env = dict(os.environ)
    env["PYTHONPATH"] = str(root / "src")
    for name in [
        "stable_partition_basic.py",
        "cover_basic.py",
        "geometry_validation_basic.py",
        "residual_sampler_research_demo.py",
    ]:
        completed = subprocess.run(
            [sys.executable, str(root / "examples" / name)],
            cwd=root,
            env=env,
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert completed.returncode == 0, completed.stderr
