import os
import logging
import requests
from datetime import datetime

from pyspark.sql import SparkSession
import pyspark.sql.functions as F

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "minioadmin")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "minioadmin")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

AQI_API_KEY = os.getenv("AQI_API_KEY", "e048e3775de428db37a3ce2a329bb7b7217c1d7f")

logger = logging.getLogger(__name__)

INPUT_FILE = "dags/data/cities.csv"

def get_aqi_data_by_city(slug):
    logger.info(f"Getting AQI data for city: {slug}...")
    try:
        url = f"https://api.waqi.info/feed/{slug}/?token={AQI_API_KEY}"
        response = requests.get(url)
        result = response.json()

        if response.status_code == 200 and result.get("status") == "ok":
            logger.info(f"Successfully got AQI data for city: {slug}")
            print(f"Successfully got AQI data for city: {slug}")
            data = result.get("data")
            data["slug"] = slug
            return data
        else:
            logger.error(f"Failed to get AQI data for city: {slug}")
            print(f"Failed to get AQI data for city: {slug}")
            return None
    except Exception as e:
        logger.error(f"Failed to get AQI data for city: {slug}: {e}")
        print(f"Failed to get AQI data for city: {slug}: {e}")
        return None


spark = (
    SparkSession.builder
    .appName("Create or Skip City")
    .config("spark.master", "spark://spark-master:7077")
    .config("spark.sql.extensions",
            "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions,"
            "org.projectnessie.spark.extensions.NessieSparkSessionExtensions")
    .config("spark.sql.defaultCatalog", "nessie")
    .config("spark.sql.catalog.nessie", "org.apache.iceberg.spark.SparkCatalog")
    .config("spark.sql.catalog.nessie.catalog-impl", "org.apache.iceberg.nessie.NessieCatalog")
    .config("spark.sql.catalog.nessie.uri", "http://nessie:19120/api/v1")
    .config("spark.sql.catalog.nessie.ref", "main")
    .config("spark.sql.catalog.nessie.warehouse", "s3://warehouse/")
    .config("spark.sql.catalog.nessie.authentication.type", "NONE")
    .config("spark.sql.catalog.nessie.io-impl", "org.apache.iceberg.aws.s3.S3FileIO")
    .config("spark.sql.catalog.nessie.s3.endpoint", "http://minio:9000")
    .config("spark.sql.catalog.nessie.s3.path-style-access", "true")
    .config("spark.sql.catalog.nessie.s3.region", AWS_REGION)
    .config("spark.sql.catalog.nessie.s3.access-key-id", AWS_ACCESS_KEY_ID)
    .config("spark.sql.catalog.nessie.s3.secret-access-key", AWS_SECRET_ACCESS_KEY)
    .getOrCreate()
)

try:
    data = []
    cities = spark.sql("SELECT * FROM nessie.bronze.cities WHERE slug IS NOT NULL")

    if not cities:
        logger.error(f"No cities found")
        print(f"No cities found")
        raise Exception("No cities found")

    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    logger.info(f"Processing {len(cities.collect())} cities")
    for row in cities.collect():
        aqi_data = get_aqi_data_by_city(row.slug)
        if not aqi_data:
            logger.error(f"No AQI data found for city: {row.city}")
            print(f"No AQI data found for city: {row.city}")
            continue

        data.append({
            "timestamp": timestamp,
            "payload": aqi_data,
        })


    if len(data) > 0:
        df = spark.createDataFrame(data)
        df = df.withColumn("date", F.to_date(F.to_timestamp("timestamp")))

        df.writeTo("nessie.raw.aqi").partitionedBy("date").createOrReplace()

        logger.info(f"AQI Ingested for date: {timestamp}")
        print(f"AQI Ingested for date: {timestamp}")
    else:
        logger.error(f"No AQI data found")
        print(f"No AQI data found for date: {timestamp}")
        raise Exception("No AQI data found")

except Exception as e:
    logger.error(f"Error during Iceberg check: {e}")
    print(f"Error during Iceberg check: {e}")
    raise

finally:
    spark.stop()