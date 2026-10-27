from pathlib import Path

_PATH = Path(__file__).resolve().parent / "data" / "equipment.txt"

def _load():
    with open(_PATH, encoding="utf-8") as f:
        return frozenset(
            line.strip().lower()
            for line in f
            if line.strip() and not line.startswith("#")
        )

EQUIPMENT = _load()