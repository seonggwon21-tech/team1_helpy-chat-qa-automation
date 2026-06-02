"""Run CI pytest targets and export the exit code for later jobs."""

import os
import subprocess
import sys


TEST_TARGETS = [
    "tests/test_lessonplan_create.py",
    "tests/test_model_change.py",
    "tests/test_search.py",
]


def main():
    command = [sys.executable, "-m", "pytest", *TEST_TARGETS]
    completed = subprocess.run(command, check=False)
    exit_code = completed.returncode

    with open("test_status.env", "w", encoding="utf-8") as env_file:
        env_file.write(f"TEST_EXIT_CODE={exit_code}\n")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
