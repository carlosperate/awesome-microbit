#!/usr/bin/env python3
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE_DIR = ROOT / "site_src"
SOURCE_FILES = (
    "README.md",
    "contributing.md",
    "code-of-conduct.md",
)
CLEAN_AFTER_BUILD = True


def main() -> int:
    if SOURCE_DIR.exists():
        shutil.rmtree(SOURCE_DIR)
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)

    for file_name in SOURCE_FILES:
        source_path = ROOT / file_name
        if not source_path.is_file():
            print(f"Missing source file: {source_path}", file=sys.stderr)
            exit(1)
        shutil.copy2(source_path, SOURCE_DIR / file_name)

    try:
        subprocess.run(["mkdocs", "build"], cwd=ROOT, check=True)
    except subprocess.CalledProcessError as exc:
        print(f"mkdocs build failed with exit code {exc.returncode}", file=sys.stderr)
        print(f"Temporary docs folder kept at: {SOURCE_DIR}", file=sys.stderr)
        exit(exc.returncode)

    if CLEAN_AFTER_BUILD:
        shutil.rmtree(SOURCE_DIR)
        print("mkdocs build completed successfully. Removed temporary docs folder.")
    else:
        print(f"mkdocs build completed successfully. Temporary docs folder kept at: {SOURCE_DIR}")


if __name__ == "__main__":
    main()
