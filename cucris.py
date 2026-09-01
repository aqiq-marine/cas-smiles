import os
from pathlib import Path

import requests


class CucrisClient:
    BASE_URL = "https://www.chiba-cucris.jp/cris_v3_0"

    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/151.0.0.0 Safari/537.36"
    )

    def __init__(
        self,
        user_id: str | None = None,
        password: str | None = None,
    ):
        self.user_id = user_id or os.environ["CUCRIS_USER_ID"]
        self.password = password or os.environ["CUCRIS_PASSWORD"]

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": self.USER_AGENT,
        })

    def login(self) -> None:
        """CUCRISにログインする。"""

        login_url = f"{self.BASE_URL}/User/Login"

        # ログインページを取得してセッションを確立
        r = self.session.get(login_url)
        r.raise_for_status()

        # ログイン
        r = self.session.post(
            login_url,
            headers={
                "Referer": login_url,
                "Origin": "https://www.chiba-cucris.jp",
            },
            data={
                "UserID": self.user_id,
                "Password": self.password,
                "Login": "ログイン",
            },
        )
        r.raise_for_status()

    def search_usage(
        self,
        group_ids: str,
        build_ids: str,
        storage_ids: str,
    ) -> requests.Response:
        """指定条件で薬品使用状況を検索する。"""

        search_url = f"{self.BASE_URL}/Chemical/SearchUsage"

        # SearchUsageページ
        r = self.session.get(
            search_url,
            headers={
                "Referer": f"{self.BASE_URL}/Portal/Index",
            },
        )
        r.raise_for_status()

        # 検索条件をセット
        r = self.session.post(
            f"{self.BASE_URL}/Chemical/GetSearchUsageList",
            headers={
                "Referer": search_url,
                "Origin": "https://www.chiba-cucris.jp",
                "X-Requested-With": "XMLHttpRequest",
            },
            data={
                "SearchGroupIDs": group_ids,
                "SearchBuildIDs": build_ids,
                "SearchStorageIDs": storage_ids,
            },
        )
        r.raise_for_status()

        return r

    def download_csv(
        self,
        output_path: str | Path = "StockList.csv",
    ) -> Path:
        """現在の検索条件に対応するCSVを取得して保存する。"""

        r = self.session.post(
            f"{self.BASE_URL}/Chemical/SearchUsageExport",
            headers={
                "Referer": f"{self.BASE_URL}/Chemical/SearchUsage",
                "Origin": "https://www.chiba-cucris.jp",
            },
            data={
                "Csv": "",
            },
        )
        r.raise_for_status()

        # CP932 → UTF-8
        csv_text = r.content.decode("cp932")

        output_path = Path(output_path)
        output_path.write_text(
            csv_text,
            encoding="utf-8",
            newline="",
        )

        return output_path

    def get_stock_list(
        self,
        group_ids: str,
        build_ids: str,
        storage_ids: str,
        output_path: str | Path = "StockList.csv",
    ) -> Path:
        """ログインからCSV取得までを一括して行う。"""

        self.login()

        self.search_usage(
            group_ids=group_ids,
            build_ids=build_ids,
            storage_ids=storage_ids,
        )

        return self.download_csv(output_path)
