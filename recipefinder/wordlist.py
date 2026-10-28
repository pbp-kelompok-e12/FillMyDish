from pathlib import Path

_PATH = Path(__file__).resolve().parent / "data" / "equipment.txt"

def _load():
    items = set()
    with open(_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip().lower()
            if not line or line.startswith("#"):
                continue
            items.add(line)              
            items.update(line.split()) 
    return frozenset(items)
EQUIPMENT = _load()