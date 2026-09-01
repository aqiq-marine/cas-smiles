import io
import os

import pandas as pd
import requests


class CucrisClient:
    BASE_URL = "https://www.chiba-cucris.jp/cris_v3_0"

    def __init__(
        self,
        user_id: str | None = None,
        password: str | None = None,
    ):
        self.user_id = user_id or os.environ["CUCRIS_USER_ID"]
        self.password = password or os.environ["CUCRIS_PASSWORD"]

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/151.0.0.0 Safari/537.36"
            )
        })

    def login(self) -> None:
        login_url = f"{self.BASE_URL}/User/Login"

        r = self.session.get(login_url)
        r.raise_for_status()

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
    ) -> None:
        search_url = f"{self.BASE_URL}/Chemical/SearchUsage"

        r = self.session.get(
            search_url,
            headers={
                "Referer": f"{self.BASE_URL}/Portal/Index",
            },
        )
        r.raise_for_status()

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

    def download_csv(self) -> pd.DataFrame:
        """現在の検索条件に対応する在庫データを取得する。"""
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

        return pd.read_csv(
            io.BytesIO(r.content),
            encoding="cp932",
        )

    def get_stock_list(
        self,
        group_ids: str,
        build_ids: str,
        storage_ids: str,
    ) -> pd.DataFrame:
        """CUCRISから在庫一覧を取得する。"""
        self.login()

        self.search_usage(
            group_ids=group_ids,
            build_ids=build_ids,
            storage_ids=storage_ids,
        )

        return self.download_csv()
