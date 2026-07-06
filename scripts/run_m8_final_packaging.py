from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from failsafemlx.packaging.final_artifacts import generate_m8_artifacts


def main() -> None:
    summary = generate_m8_artifacts(ROOT)
    for relative_path in summary["written_paths"]:
        print(f"Wrote {ROOT / relative_path}")
    print("M8 completed successfully.")


if __name__ == "__main__":
    main()
