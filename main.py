import json
import sys
from pathlib import Path

import pandas as pd

from cucris import CucrisClient
from cas_compare import find_unknown_cas
from cas_smiles import add_smiles


OUTPUT_COLUMNS = ("cas", "smiles", "name", "location", "amount", "supplier")
LATEST_DATE_COLUMNS = ("登録日時", "入庫日", "開封日", "使用日時")


def clean(value) -> str:
    return "" if pd.isna(value) else str(value).strip()


def latest_stock_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Return one, newest row for each CAS number."""
    result = df.copy()
    result["_cas_normalized"] = result["CAS番号"].map(clean)
    result = result[result["_cas_normalized"] != ""].copy()

    available_dates = [
        column for column in LATEST_DATE_COLUMNS if column in result.columns
    ]
    if available_dates:
        parsed_dates = result[available_dates].apply(
            pd.to_datetime,
            errors="coerce",
        )
        result["_latest_date"] = parsed_dates.max(axis=1)
        # Stable sorting preserves the original order when dates are equal
        # or unavailable.
        result = result.sort_values("_latest_date", kind="stable")

    result = result.drop_duplicates("_cas_normalized", keep="last")
    return result.drop(columns=["_cas_normalized", "_latest_date"], errors="ignore")


def convert_inventory(df: pd.DataFrame, smiles_by_cas: dict[str, str], shelves_path: Path) -> pd.DataFrame:
    with shelves_path.open(encoding="utf-8") as stream:
        shorten_shelf = json.load(stream)

    rows = []
    for _, row in df.iterrows():
        cas = clean(row.get("CAS番号"))
        if not cas:
            continue

        # 1. 「容量」と「容量単位」を最優先で見る
        volume = clean(row.get("容量"))
        volume_unit = clean(row.get("容量単位"))
        if volume:
            amount = f"{volume} {volume_unit}".strip()
        else:
            # 2. 次に「在庫量」と「在庫量単位」を見る
            amount = clean(row.get("在庫量"))
            unit = clean(row.get("在庫量単位"))
            if amount:
                amount = f"{amount} {unit}".strip()
            else:
                # 3. 最後に「使用前重量(g)」を見る
                weight = clean(row.get("使用前重量(g)"))
                amount = f"{weight} g" if weight else ""

        location = clean(row.get("保管庫名（日）"))
        rows.append({
            "cas": cas,
            "smiles": smiles_by_cas.get(cas, ""),
            "name": clean(row.get("化学物質製品名（日）")),
            "location": shorten_shelf.get(location, location),
            "amount": amount,
            "supplier": clean(row.get("製造元名（英）")),
        })

    return pd.DataFrame(rows, columns=OUTPUT_COLUMNS)


def main() -> int:
    project_dir = Path(__file__).parent
    cas_smiles_path = project_dir / "cas_smiles.csv"
    shelves_path = project_dir.parent / "shelves.json"
    output_path = Path(sys.argv[1]) if len(sys.argv) > 1 else project_dir.parent / "inventory.csv"

    client = CucrisClient()

    df = client.get_stock_list(
        group_ids="266",
        build_ids="1,7,14",
        storage_ids="362,1220,1222",
    )
    print(df)
    df = latest_stock_rows(df)

    # 参照DBに存在しないCASを抽出
    unknown = find_unknown_cas(
        df,
        cas_smiles_path,
    )

    # 未登録CASだけPubChemからSMILES取得
    new_results, failed = add_smiles(unknown)

    reference = pd.read_csv(cas_smiles_path, dtype=str)
    smiles_by_cas = dict(
        zip(
            reference["cas"].astype(str).str.strip(),
            reference["smiles"].fillna(""),
        )
    )
    smiles_by_cas.update(
        dict(
            zip(
                new_results["CAS番号"].astype(str).str.strip(),
                new_results["smiles"].fillna(""),
            )
        )
    )

    converted = convert_inventory(df, smiles_by_cas, shelves_path)
    converted.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig",
    )

    print(f"Saved {len(converted)} rows to {output_path}")
    if not failed.empty:
        print(f"SMILES not found for {len(failed)} CAS numbers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
