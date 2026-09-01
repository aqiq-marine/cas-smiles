import os
import requests

BASE = "https://www.chiba-cucris.jp/cris_v3_0"

USER_ID = os.environ["CUCRIS_USER_ID"]
PASSWORD = os.environ["CUCRIS_PASSWORD"]

session = requests.Session()

session.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/151.0.0.0 Safari/537.36"
    )
})

# 1. ログインページ
session.get(f"{BASE}/User/Login")

# 2. ログイン
r = session.post(
    f"{BASE}/User/Login",
    headers={
        "Referer": f"{BASE}/User/Login",
        "Origin": "https://www.chiba-cucris.jp",
    },
    data={
        "UserID": USER_ID,
        "Password": PASSWORD,
        "Login": "ログイン",
    },
)

r.raise_for_status()

# 3. SearchUsageページ
r = session.get(
    f"{BASE}/Chemical/SearchUsage",
    headers={
        "Referer": f"{BASE}/Portal/Index",
    },
)

r.raise_for_status()

# 4. 検索条件をセット
r = session.post(
    f"{BASE}/Chemical/GetSearchUsageList",
    headers={
        "Referer": f"{BASE}/Chemical/SearchUsage",
        "Origin": "https://www.chiba-cucris.jp",
        "X-Requested-With": "XMLHttpRequest",
    },
    data={
        "SearchGroupIDs": "266",
        "SearchBuildIDs": "1,7,14",
        "SearchStorageIDs": "362,1220,1222",
    },
)

r.raise_for_status()

# 5. CSV取得
r = session.post(
    f"{BASE}/Chemical/SearchUsageExport",
    headers={
        "Referer": f"{BASE}/Chemical/SearchUsage",
        "Origin": "https://www.chiba-cucris.jp",
    },
    data={
        "Csv": "",
    },
)

r.raise_for_status()

# CP932 → UTF-8 に変換して保存
csv_text = r.content.decode("cp932")

with open("StockList.csv", "w", encoding="utf-8", newline="") as f:
    f.write(csv_text)

print("CSV saved:", len(csv_text), "characters")

