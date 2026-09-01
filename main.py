from cucris import CucrisClient
from cas_compare import find_unknown_cas
from cas_smiles import add_smiles


def main():
    client = CucrisClient()

    df = client.get_stock_list(
        group_ids="266",
        build_ids="1,7,14",
        storage_ids="362,1220,1222",
    )

    # 参照DBに存在しないCASを抽出
    unknown = find_unknown_cas(
        df,
        "cas_smiles.csv",
    )

    # 未登録CASだけPubChemからSMILES取得
    results, failed = add_smiles(unknown)

    results.to_csv(
        "new_cas_smiles.csv",
        index=False,
        encoding="utf-8-sig",
    )

    failed.to_csv(
        "failed_cas.csv",
        index=False,
        encoding="utf-8-sig",
    )


if __name__ == "__main__":
    main()
