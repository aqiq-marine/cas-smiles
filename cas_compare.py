from pathlib import Path

import pandas as pd


def find_unknown_cas(
    df: pd.DataFrame,
    cas_smiles_path: str | Path,
    *,
    df_cas_column: str = "CAS番号",
    reference_cas_column: str = "CAS",
) -> pd.DataFrame:
    """
    参照DBに存在しないCAS番号を持つ行を抽出する。

    Parameters
    ----------
    df:
        CUCRISから取得したDataFrame。
    cas_smiles_path:
        CAS番号とSMILESの対応表CSV。
    df_cas_column:
        CUCRIS DataFrameのCAS番号列。
    reference_cas_column:
        参照DBのCAS番号列。

    Returns
    -------
    pd.DataFrame
        参照DBに存在しないCAS番号を持つ、
        CUCRIS DataFrameの行。
    """

    reference_df = pd.read_csv(
        cas_smiles_path,
        dtype=str,
    )

    df_cas = (
        df[df_cas_column]
        .astype("string")
        .str.strip()
    )

    reference_cas = (
        reference_df[reference_cas_column]
        .astype("string")
        .str.strip()
    )

    reference_set = set(reference_cas.dropna())

    mask = (
        df_cas.notna()
        & ~df_cas.isin(reference_set)
    )

    return df.loc[mask].copy()
