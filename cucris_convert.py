"""Convert a CUCris export to the application's compact inventory CSV.

Usage:
    python cucris_convert.py cuc ris.csv inventory.csv
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


OUTPUT_FIELDS = ("cas", "smiles", "name", "location", "amount", "supplier")


def clean(value: str | None) -> str:
    return (value or "").strip()


def load_smiles(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        for row in reader:
            cas = clean(row.get("cas") or row.get("CAS") or row.get("CAS番号"))
            smiles = clean(row.get("smiles") or row.get("SMILES"))
            if cas:
                result[cas] = smiles
    return result


def load_shelf_short_names(path: Path | None) -> dict[str, str]:
    """Load the Japanese storage-name to short-name mapping if available."""
    if path is None or not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as stream:
        mapping = json.load(stream)
    if not isinstance(mapping, dict):
        raise ValueError(f"shelf mapping must be a JSON object: {path}")
    return {str(name): str(short_name) for name, short_name in mapping.items()}


def inventory_amount(row: dict[str, str]) -> str:
    # 1. 「容量」と「容量単位」を最優先で見る
    volume = clean(row.get("容量"))
    volume_unit = clean(row.get("容量単位"))
    if volume:
        return f"{volume} {volume_unit}".strip()

    # 2. 次に「在庫量」と「在庫量単位」を見る
    amount = clean(row.get("在庫量"))
    unit = clean(row.get("在庫量単位"))
    if amount:
        return f"{amount} {unit}".strip()

    # 3. 最後に「使用前重量(g)」を見る
    weight = clean(row.get("使用前重量(g)"))
    return f"{weight} g" if weight else ""


def convert(
    source: Path,
    smiles_path: Path,
    destination: Path,
    shelves_path: Path | None = None,
) -> None:
    smiles_by_cas = load_smiles(smiles_path)
    if shelves_path is None:
        shelves_path = Path(__file__).parent.parent / "shelves.json"
    shorten_shelf = load_shelf_short_names(shelves_path)
    with source.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        with destination.open("w", encoding="utf-8", newline="") as output:
            writer = csv.DictWriter(output, fieldnames=OUTPUT_FIELDS)
            writer.writeheader()
            for row in reader:
                cas = clean(row.get("CAS番号"))
                if not cas:
                    continue
                location = clean(row.get("保管庫名（日）"))
                writer.writerow(
                    {
                        "cas": cas,
                        "smiles": smiles_by_cas.get(cas, ""),
                        "name": clean(row.get("化学物質製品名（日）")),
                        "location": shorten_shelf.get(location, location),
                        "amount": inventory_amount(row),
                        "supplier": clean(row.get("製造元名（英）")),
                    }
                )


def main() -> int:
    if len(sys.argv) not in (2, 3):
        print("usage: python cucris_convert.py CUCris.csv [output.csv]", file=sys.stderr)
        return 2
    source = Path(sys.argv[1])
    destination = Path(sys.argv[2]) if len(sys.argv) == 3 else source.with_name("reagent.csv")
    smiles_path = Path(__file__).with_name("cas_smiles.csv")
    shelves_path = Path(__file__).parent.parent / "shelves.json"
    convert(source, smiles_path, destination, shelves_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
