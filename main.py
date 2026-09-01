from cucris import CucrisClient


def main():
    client = CucrisClient()

    df = client.get_stock_list(
        group_ids="266",
        build_ids="1,7,14",
        storage_ids="362,1220,1222",
    )

    print(df)
    print(df.columns)


if __name__ == "__main__":
    main()
