"""Convert a CUCris export to the application's compact inventory CSV.

Usage:
    python cucris_convert.py cuc ris.csv inventory.csv
"""

from __future__ import annotations

import csv
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


def inventory_amount(row: dict[str, str]) -> str:
    # CUCris exports inventory as either a numeric amount with a unit or
    # the measured pre-use weight. Prefer the explicit amount when present.
    amount = clean(row.get("在庫量"))
    unit = clean(row.get("在庫量単位"))
    if amount:
        return f"{amount} {unit}".strip()

    weight = clean(row.get("使用前重量(g)"))
    return f"{weight} g" if weight else ""


def convert(source: Path, smiles_path: Path, destination: Path) -> None:
    smiles_by_cas = load_smiles(smiles_path)
    with source.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        with destination.open("w", encoding="utf-8", newline="") as output:
            writer = csv.DictWriter(output, fieldnames=OUTPUT_FIELDS)
            writer.writeheader()
            for row in reader:
                cas = clean(row.get("CAS番号"))
                if not cas:
                    continue
                writer.writerow(
                    {
                        "cas": cas,
                        "smiles": smiles_by_cas.get(cas, ""),
                        "name": clean(row.get("化学物質製品名（日）")),
                        "location": clean(row.get("保管庫名（日）")),
                        "amount": inventory_amount(row),
                        "supplier": "",
                    }
                )


def main() -> int:
    if len(sys.argv) not in (2, 3):
        print("usage: python cucris_convert.py CUCris.csv [output.csv]", file=sys.stderr)
        return 2
    source = Path(sys.argv[1])
    destination = Path(sys.argv[2]) if len(sys.argv) == 3 else source.with_name("inventory.csv")
    smiles_path = Path(__file__).with_name("cas_smiles.csv")
    convert(source, smiles_path, destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
