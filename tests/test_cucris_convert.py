import csv
import tempfile
import unittest
from pathlib import Path

from cucris_convert import convert


class ConvertTest(unittest.TestCase):
    def test_convert_inventory_rows(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "cucris.csv"
            smiles = root / "cas_smiles.csv"
            output = root / "inventory.csv"

            with smiles.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=("cas", "smiles"))
                writer.writeheader()
                writer.writerow({"cas": "50-00-0", "smiles": "C=O"})

            fields = (
                "CAS番号",
                "化学物質製品名（日）",
                "保管庫名（日）",
                "使用前重量(g)",
            )
            with source.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=fields)
                writer.writeheader()
                writer.writerow(
                    {
                        "CAS番号": "50-00-0",
                        "化学物質製品名（日）": "ホルムアルデヒド液",
                        "保管庫名（日）": "毒劇物庫",
                        "使用前重量(g)": "500",
                    }
                )
                writer.writerow({"CAS番号": "", "化学物質製品名（日）": "空欄"})

            convert(source, smiles, output)

            with output.open(encoding="utf-8", newline="") as stream:
                rows = list(csv.DictReader(stream))

            self.assertEqual(
                rows,
                [
                    {
                        "cas": "50-00-0",
                        "smiles": "C=O",
                        "name": "ホルムアルデヒド液",
                        "location": "毒劇物庫",
                        "amount": "500 g",
                        "supplier": "",
                    }
                ],
            )


if __name__ == "__main__":
    unittest.main()
