import os
import sys
import boto3
import pandas as pd
from sqlalchemy import create_engine
from io import StringIO

S3_BUCKET       = os.environ.get("S3_BUCKET")
S3_KEY          = os.environ.get("S3_KEY")

RDS_HOST        = os.environ.get("RDS_HOST")
RDS_PORT        = os.environ.get("RDS_PORT", "3306")
RDS_USER        = os.environ.get("RDS_USER")
RDS_PASSWORD    = os.environ.get("RDS_PASSWORD")
RDS_DB_NAME     = os.environ.get("RDS_DB_NAME")
RDS_TABLE_NAME  = os.environ.get("RDS_TABLE_NAME", "student_data")

GLUE_DB_NAME    = os.environ.get("GLUE_DB_NAME", "fallback_db")
GLUE_TABLE_NAME = os.environ.get("GLUE_TABLE_NAME", "fallback_table")
GLUE_S3_LOCATION = os.environ.get("GLUE_S3_LOCATION")

AWS_REGION      = os.environ.get("AWS_REGION", "us-east-1")


def read_csv_from_s3(bucket, key):
    print(f"[INFO] Reading s3://{bucket}/{key} ...")
    s3 = boto3.client("s3", region_name=AWS_REGION)
    obj = s3.get_object(Bucket=bucket, Key=key)
    csv_content = obj["Body"].read().decode("utf-8")
    df = pd.read_csv(StringIO(csv_content))
    print(f"[INFO] Loaded {len(df)} rows from S3.")
    return df


def push_to_rds(df):
    print(f"[INFO] Attempting to connect to RDS at {RDS_HOST} ...")
    conn_str = f"mysql+pymysql://{RDS_USER}:{RDS_PASSWORD}@{RDS_HOST}:{RDS_PORT}/{RDS_DB_NAME}"
    engine = create_engine(conn_str, connect_args={"connect_timeout": 10})

    with engine.connect() as connection:
        df.to_sql(RDS_TABLE_NAME, con=connection, if_exists="append", index=False)

    print(f"[SUCCESS] Inserted {len(df)} rows into RDS table '{RDS_TABLE_NAME}'.")


def fallback_to_glue():
    print("[WARNING] RDS push failed. Falling back to AWS Glue Data Catalog...")
    glue = boto3.client("glue", region_name=AWS_REGION)

    try:
        glue.create_database(DatabaseInput={"Name": GLUE_DB_NAME})
        print(f"[INFO] Created Glue database '{GLUE_DB_NAME}'.")
    except glue.exceptions.AlreadyExistsException:
        print(f"[INFO] Glue database '{GLUE_DB_NAME}' already exists.")

    try:
        glue.create_table(
            DatabaseName=GLUE_DB_NAME,
            TableInput={
                "Name": GLUE_TABLE_NAME,
                "StorageDescriptor": {
                    "Columns": [
                        {"Name": "col1", "Type": "string"},
                        {"Name": "col2", "Type": "string"},
                    ],
                    "Location": GLUE_S3_LOCATION,
                    "InputFormat": "org.apache.hadoop.mapred.TextInputFormat",
                    "OutputFormat": "org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat",
                    "SerdeInfo": {
                        "SerializationLibrary": "org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe",
                        "Parameters": {"field.delim": ","},
                    },
                },
                "TableType": "EXTERNAL_TABLE",
                "Parameters": {"classification": "csv"},
            },
        )
        print(f"[SUCCESS] Created Glue table '{GLUE_TABLE_NAME}' pointing to {GLUE_S3_LOCATION}.")
    except glue.exceptions.AlreadyExistsException:
        print(f"[INFO] Glue table '{GLUE_TABLE_NAME}' already exists. Skipping creation.")


def main():
    required = [S3_BUCKET, S3_KEY, RDS_HOST, RDS_USER, RDS_PASSWORD, RDS_DB_NAME]
    if not all(required):
        print("[ERROR] Missing one or more required environment variables.")
        sys.exit(1)

    df = read_csv_from_s3(S3_BUCKET, S3_KEY)

    try:
        push_to_rds(df)
    except Exception as e:
        print(f"[ERROR] RDS push failed: {e}")
        fallback_to_glue()


if __name__ == "__main__":
    main()
