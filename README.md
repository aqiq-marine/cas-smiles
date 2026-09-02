# CAS-SMILES / CUCris CSV変換ツール

CUCrisから出力した化学物質管理CSVを、CAS番号・SMILES・保管場所・在庫量を持つ簡潔なCSVへ変換するためのプロジェクトです。

## 変換後の形式

出力される列は次の6列です。

```csv
cas,smiles,name,location,amount,supplier
```

| 出力列 | 入力元・内容 |
| --- | --- |
| `cas` | `CAS番号` |
| `smiles` | `cas_smiles.csv`からCAS番号で検索 |
| `name` | `化学物質製品名（日）` |
| `location` | `保管庫名（日）`を`shelves.json`の対応表で短縮（未登録は元の名前） |
| `amount` | `使用前重量(g)`を在庫量として使用 |
| `supplier` | 空文字 |

CAS番号が空欄の行は出力しません。SMILESが見つからない場合は空欄になります。
同じCAS番号が複数ある場合は、`登録日時`、`入庫日`、`開封日`、`使用日時`のうち最も新しい日時を持つ行を採用し、CAS番号ごとに1行だけ出力します。

## 使い方

CUCrisのCSVをプロジェクト直下に置き、次のコマンドを実行します。

```powershell
python cucris_convert.py CUCris.csv inventory.csv
```

出力先を省略した場合は、入力ファイルと同じ場所に`inventory.csv`を作成します。

```powershell
python cucris_convert.py CUCris.csv
```

SMILES検索用の`cas_smiles.csv`は、`cucris_convert.py`と同じディレクトリに配置してください。CSVはUTF-8（BOM付きも可）で読み込み、出力はUTF-8で書き込みます。

保管庫名の短縮対応表は、プロジェクトディレクトリの1つ上に`shelves.json`として配置してください。例：

```json
{
  "毒劇物庫": "毒劇物",
  "冷蔵庫": "冷蔵"
}
```

## テスト

標準ライブラリの`unittest`を使用しています。

```powershell
python -m unittest discover -s tests -v
```

テストでは、CAS番号によるSMILES検索、各列の変換、空の`supplier`、CAS番号空欄行のスキップを確認します。

## ファイル構成

```text
cas_smiles.csv                 CAS番号とSMILESの対応表
cucris_convert.py              CUCris CSVの変換処理
tests/test_cucris_convert.py   変換処理のテスト
```
