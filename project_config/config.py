import os

from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

DEFAULT_ARGS = {
    'owner': 'swift',
    'retries': 0,
    'retry_delay': timedelta(seconds=600),
}

# MINIOS S3 CREDENTIALS
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_BUCKET = os.getenv("MINIO_BUCKET")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET")
MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"