import os
import logging

from pyspark.sql import SparkSession

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "minioadmin")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "minioadmin")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

logger = logging.getLogger(__name__)

INPUT_FILE = "dags/data/cities.csv"

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
    spark.sql("CREATE NAMESPACE IF NOT EXISTS nessie.raw")
    spark.sql("CREATE NAMESPACE IF NOT EXISTS nessie.bronze")
    spark.sql("CREATE NAMESPACE IF NOT EXISTS nessie.silver")
    spark.sql("CREATE NAMESPACE IF NOT EXISTS nessie.gold")
    
    tables = spark.sql("SHOW TABLES IN nessie.bronze").collect()
    exists = any(t.tableName == "cities" for t in tables)

    valid_cities = []
    if not exists:      
        logger.info(f"Table cities does not exist — creating and ingesting data...")
        print("Table cities does not exist — creating and ingesting data...")

        cities = spark.read.option("header", "true").option("sep", ",").csv(INPUT_FILE)
        for row in cities.collect():
            valid_cities.append({
                "city": row.city,
                "country": row.country,
                "population": row.population,
                "slug": row.slug,
            })
        
        df = spark.createDataFrame(valid_cities)
        df.writeTo("nessie.bronze.cities").createOrReplace()

        logger.info(f"Table cities created and data ingested")
        print(f"Table cities created and data ingested")
    else:
        logger.info("Table cities already exists")
        print("Table cities already exists")

except Exception as e:
    logger.error(f"Error during Iceberg check: {e}")
    print(f"Error during Iceberg check: {e}")
    raise

finally:
    spark.stop()