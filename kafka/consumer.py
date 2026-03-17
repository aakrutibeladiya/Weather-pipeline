import json
import boto3
import os
from kafka import KafkaConsumer
from datetime import datetime, timezone
from dotenv import load_dotenv
load_dotenv() 

# AWS config from environment variables
S3_BUCKET = os.getenv("S3_BUCKET", "weather-pipeline-raw")

def get_s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
    )

def save_to_s3(s3, record):
    """Save a single weather record to S3 as a JSON file"""
    city = record["city"].lower().replace(" ", "_")
    date = record["timestamp"][:10]  # YYYY-MM-DD
    ts   = datetime.now(timezone.utc).timestamp()

    # Partitioned path: easy to query later with Redshift or Athena
    key = f"raw/city={city}/date={date}/{ts}.json"

    s3.put_object(
        Bucket=S3_BUCKET,
        Key=key,
        Body=json.dumps(record),
        ContentType="application/json",
    )
    return key

def main():
    consumer = KafkaConsumer(
        "weather-raw",
        bootstrap_servers="kafka:29092",
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset="earliest",   # Read from beginning of topic
        consumer_timeout_ms=10000,      # Stop after 10s of no messages
        group_id="weather-s3-consumer",
    )

    s3 = get_s3_client()
    print("Consumer started — reading from Kafka topic: weather-raw")
    count = 0

    for message in consumer:
        record = message.value
        try:
            key = save_to_s3(s3, record)
            print(f"✅ Saved: {record['city']} → s3://{S3_BUCKET}/{key}")
            count += 1
        except Exception as e:
            print(f"❌ Failed to save {record.get('city', '?')}: {e}")

    print(f"\n Consumer done. {count} records saved to S3.")

if __name__ == "__main__":
    main()