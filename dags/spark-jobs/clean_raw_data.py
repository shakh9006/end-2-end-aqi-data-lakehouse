import os
import logging

from pyspark.sql import SparkSession
import pyspark.sql.functions as F

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "minioadmin")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "minioadmin")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

logger = logging.getLogger(__name__)

spark = (
    SparkSession.builder
    .appName("Clean Raw Data")
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
    tables = spark.sql("SHOW TABLES IN nessie.bronze").collect()
    exists = any(t.tableName == "aqi_daily" for t in tables)

    print("exists: ", exists)
    aqi_data = None

    if not exists:
        print("In if")
        aqi_data = spark.sql("SELECT * FROM nessie.raw.aqi")
    else:
        print("In else")
        aqi = spark.sql("SELECT MAX(timestamp) FROM nessie.bronze.aqi_daily")
        latest_date = aqi.collect()[0][0]

        print(f"Latest AQI data timestamp: {latest_date}")
        if latest_date:
            aqi_data = spark.sql(f"SELECT * FROM nessie.raw.aqi WHERE timestamp > '{latest_date}'")
            aqi_data.show(truncate=False)
        else:
            aqi_data = spark.sql("SELECT * FROM nessie.raw.aqi")

    aqi_data_len = aqi_data.count()
    print("aqi_data_len: ", aqi_data_len)
    if aqi_data_len > 0:
        df = (
            aqi_data
            .withColumn("dominentpol", F.col("payload")["dominentpol"])
            .withColumn("aqi",  F.col("payload")["aqi"])
            .withColumn("pm25", F.regexp_extract(F.col("payload")["iaqi"], r"pm25=\{v=([^}]+)\}", 1).cast("double"))
            .withColumn("pm10", F.regexp_extract(F.col("payload")["iaqi"], r"pm10=\{v=([^}]+)\}", 1).cast("double"))
            .withColumn("no2",  F.regexp_extract(F.col("payload")["iaqi"], r"no2=\{v=([^}]+)\}", 1).cast("double"))
            .withColumn("o3", F.regexp_extract(F.col("payload")["iaqi"], r"o3=\{v=([^}]+)\}", 1).cast("double"))
            .withColumn("so2", F.regexp_extract(F.col("payload")["iaqi"], r"so2=\{v=([^}]+)\}", 1).cast("double"))
            .withColumn("co", F.regexp_extract(F.col("payload")["iaqi"], r"co=\{v=([^}]+)\}", 1).cast("double"))
            .withColumn("slug", F.col("payload")["slug"])
        )
        
        df = df.select(
            F.col("date"),
            F.col("timestamp"),
            F.when(F.col("aqi") == "-", "0").otherwise(F.col("aqi")).alias("aqi"),
            F.when(F.col("dominentpol") == "", "pm25").otherwise(F.col("dominentpol")).alias("dominentpol"),
            F.when(F.col("pm25").isNull(), 0).otherwise(F.col("pm25")).alias("pm25"),
            F.when(F.col("pm10").isNull(), 0).otherwise(F.col("pm10")).alias("pm10"),
            F.when(F.col("no2").isNull(), 0).otherwise(F.col("no2")).alias("no2"),
            F.when(F.col("o3").isNull(), 0).otherwise(F.col("o3")).alias("o3"),
            F.when(F.col("so2").isNull(), 0).otherwise(F.col("so2")).alias("so2"),
            F.when(F.col("co").isNull(), 0).otherwise(F.col("co")).alias("co"),
            F.col("slug"),
        )
        
        df.show(truncate=False)
        # df.writeTo("nessie.bronze.aqi_daily").partitionedBy("date").createOrReplace()

        logger.info(f"AQI data cleaned and ingested")
        print(f"AQI data cleaned and ingested")
    else:
        logger.error(f"No AQI data found")
        print(f"No AQI data found")

except Exception as e:
    logger.error(f"Error during Iceberg check: {e}")
    print(f"Error during Iceberg check: {e}")
    raise
finally:
    spark.stop()