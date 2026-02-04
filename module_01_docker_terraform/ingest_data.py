import os
import pandas as pd
import requests
import gzip
import shutil
import tempfile
from sqlalchemy import create_engine


def get_engine():
    return create_engine(
        f"postgresql+psycopg2://{os.environ['PGUSER']}:{os.environ['PGPASSWORD']}"
        f"@{os.environ['PGHOST']}:{os.environ.get('PGPORT', '5432')}/{os.environ['PGDATABASE']}"
    )


def download_file(url: str, dest_path: str):
    print(f"Downloading {url}")
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                f.write(chunk)


def ingest_csv_gz(engine, table_name, url, chunksize=100_000):
    with tempfile.TemporaryDirectory() as tmpdir:
        gz_path = os.path.join(tmpdir, "data.csv.gz")
        csv_path = os.path.join(tmpdir, "data.csv")

        download_file(url, gz_path)

        print("Unzipping CSV.GZ")
        with gzip.open(gz_path, "rb") as f_in, open(csv_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

        df_iter = pd.read_csv(csv_path, iterator=True, chunksize=chunksize)

        print("Creating table schema")
        first_chunk = next(df_iter)
        normalize_datetimes(first_chunk)
        first_chunk.head(0).to_sql(table_name, engine, if_exists="replace", index=False)
        first_chunk.to_sql(table_name, engine, if_exists="append", index=False)

        for chunk in df_iter:
            normalize_datetimes(chunk)
            chunk.to_sql(table_name, engine, if_exists="append", index=False)
            print("Inserted another chunk")


def ingest_parquet(engine, table_name, url, chunksize=100000):
    print("Reading parquet metadata")
    df = pd.read_parquet(url)

    print("Creating table schema")
    normalize_datetimes(df)
    df.head(0).to_sql(table_name, engine, if_exists="replace", index=False)

    print("Inserting parquet in chunks")
    for i in range(0, len(df), chunksize):
        chunk = df.iloc[i : i + chunksize]
        chunk.to_sql(table_name, engine, if_exists="append", index=False)
        print(f"Inserted rows {i}–{i+len(chunk)}")


def normalize_datetimes(df):
    for col in df.columns:
        if "datetime" in col:
            df[col] = pd.to_datetime(df[col], errors="coerce")


def main():
    url = os.environ["DATA_URL"]
    table_name = os.environ["TABLE_NAME"]

    engine = get_engine()

    if url.endswith(".parquet"):
        ingest_parquet(engine, table_name, url)
    elif url.endswith(".csv.gz"):
        ingest_csv_gz(engine, table_name, url)
    else:
        raise ValueError(f"Unsupported file format: {url}")


if __name__ == "__main__":
    main()
