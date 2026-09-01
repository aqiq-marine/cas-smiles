from cucris import CucrisClient


def main():
    client = CucrisClient()

    path = client.get_stock_list(
        group_ids="266",
        build_ids="1,7,14",
        storage_ids="362,1220,1222",
        output_path="StockList.csv",
    )

    print(f"CSV saved: {path}")


if __name__ == "__main__":
    main()
