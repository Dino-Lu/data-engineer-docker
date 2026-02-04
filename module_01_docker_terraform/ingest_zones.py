import os
import pandas as pd
import requests
from sqlalchemy import create_engine


def get_engine():
    return create_engine(
        f"postgresql+psycopg2://{os.environ['PGUSER']}:{os.environ['PGPASSWORD']}"
        f"@{os.environ['PGHOST']}:{os.environ.get('PGPORT', '5432')}/{os.environ['PGDATABASE']}"
    )


def download_csv(url: str) -> pd.DataFrame:
    # stream download to avoid loading entire response into memory
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        return pd.read_csv(r.raw)


def main():
    url = os.environ["ZONES_URL"]
    table_name = os.environ.get("TABLE_NAME", "taxi_zone_lookup")

    engine = get_engine()

    print(f"Downloading zones from: {url}")
    df = download_csv(url)

    # Ensure consistent column types (optional but nice)
    # LocationID should be int
    if "LocationID" in df.columns:
        df["LocationID"] = pd.to_numeric(df["LocationID"], errors="coerce").astype("Int64")

    print(f"Loading {len(df)} rows into {table_name}...")
    df.to_sql(table_name, engine, if_exists="replace", index=False)
    print("Done.")


if __name__ == "__main__":
    main()
