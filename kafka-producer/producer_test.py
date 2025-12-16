from confluent_kafka import Producer
import json

producer = Producer({
    "bootstrap.servers": "kafka:9092"   # docker 네트워크 기준
})

data = {
    "listing_id": "DUMMY_001",
    "price": 100,
    "status": "TEST",
    "lat": 1.0,
    "lng": 2.0,
    "updated_at": "2025-01-01T00:00:00"
}

producer.produce("raw.listing", json.dumps(data))
producer.flush()

print("Produced:", data)
