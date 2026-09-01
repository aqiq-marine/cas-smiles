import time

import pandas as pd
import pubchempy as pcp


def add_smiles(
    df: pd.DataFrame,
    *,
    cas_column: str = "CAS番号",
    wait: float = 0.35,
    max_retry: int = 3,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    DataFrameのCAS番号からPubChemでSMILESを取得し、
    DataFrameにsmiles列を追加する。

    PubChemで複数の候補が見つかった場合は、
    CAS番号がSynonymに登録されている最初の候補を使用する。

    Returns
    -------
    result:
        元のDataFrameに「smiles」列を追加したDataFrame。

    failed:
        SMILESを取得できなかったCAS番号のDataFrame。
    """

    result = df.copy()

    cas_list = (
        result[cas_column]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
    )

    smiles_map: dict[str, str] = {}
    failed: list[str] = []

    for i, cas in enumerate(cas_list):
        print(f"{i + 1}/{len(cas_list)} : {cas}")

        success = False

        for retry in range(max_retry):
            try:
                compounds = pcp.get_compounds(
                    cas,
                    namespace="name",
                )

                for compound in compounds:
                    synonyms = pcp.get_synonyms(compound.cid)

                    if not synonyms:
                        continue

                    syns = synonyms[0].get("Synonym", [])

                    # CAS番号が本当に登録されている候補だけを採用
                    if cas not in syns:
                        continue

                    smiles = compound.connectivity_smiles

                    if not smiles:
                        continue

                    smiles_map[cas] = smiles
                    success = True
                    break

                # APIとしては正常終了したが該当なし
                break

            except Exception as e:
                retry_wait = 2 ** retry
                print(f"Error: {e}")
                print(f"Retry in {retry_wait}s")
                time.sleep(retry_wait)

        if not success:
            failed.append(cas)

        time.sleep(wait)

    # CAS番号を正規化してSMILESを付与
    normalized_cas = (
        result[cas_column]
        .astype("string")
        .str.strip()
    )

    result["smiles"] = normalized_cas.map(smiles_map)

    failed_df = pd.DataFrame(
        {"CAS": failed}
    )

    return result, failed_df
