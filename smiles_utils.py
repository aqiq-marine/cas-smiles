"""Utilities for working with the SMILES strings used by the CSV converters."""

import re


# Atoms are either bracket expressions (for example ``[NH4+]``), two-letter
# elements, or one-letter organic/aromatic elements.  Bonds, ring numbers,
# branches, and stereochemistry are intentionally not matched.
_ATOM_TOKEN = re.compile(r"\[[^\]]+\]|Br|Cl|[BCNOFPSKIbcnosp]Se?|[H]Ar?|[A-Z][a-z]?")


def atom_count(smiles: str | None) -> int | None:
    """Return the number of atom tokens in a SMILES string.

    ``None`` is returned for an empty or unavailable SMILES so those rows can
    be placed after rows with a known atom count.
    """

    if not smiles or not smiles.strip():
        return None
    return len(_ATOM_TOKEN.findall(smiles))
