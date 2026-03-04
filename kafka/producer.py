import requests
import json
import time
from kafka import KafkaProducer
from datetime import datetime, timezone

# Cities to fetch weather for
CITIES = [
    {"name": "London",   "lat": 51.5,  "lon": -0.12},
    {"name": "New York", "lat": 40.7,  "lon": -74.0},
    {"name": "Tokyo",    "lat": 35.7,  "lon": 139.7},
]

def fetch_weather(city):
    """Fetch current weather from Open-Meteo API (no API key needed)"""
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={city['lat']}&longitude={city['lon']}"
        f"&current_weather=true"
    )
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()

    return {
        "city":           city["name"],
        "timestamp":      datetime.now(timezone.utc).isoformat(),
        "temperature_c":  data["current_weather"]["temperature"],
        "windspeed_kmh":  data["current_weather"]["windspeed"],
        "weathercode":    data["current_weather"]["weathercode"],
    }

def main():
    producer = KafkaProducer(
        bootstrap_servers="localhost:9092",
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        retries=3,
    )

    print("Producer started — fetching weather data...")

    for city in CITIES:
        try:
            message = fetch_weather(city)
            producer.send("weather-raw", value=message)
            print(f"✅ Sent: {message['city']} | {message['temperature_c']}°C | {message['timestamp']}")
        except Exception as e:
            print(f"❌ Failed for {city['name']}: {e}")

    producer.flush()
    print("All messages sent to Kafka topic: weather-raw")

if __name__ == "__main__":
    main()