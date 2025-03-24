import websocket
import time
import json
from confluent_kafka import Producer

# === Kafka Configuration ===
conf = {'SECRET'}

topic_name = 'chrish47'
producer = Producer(conf)

# === WebSocket Config ===
url = "wss://ws-feed.exchange.coinbase.com"

subscribe_msg = {
    "type": "subscribe",
    "channels": [
        {
            "name": "ticker",
            "product_ids": ["BTC-USD", "ETH-USD", "ADA-USD"]
        }
    ]
}

# Connect to WebSocket
ws = websocket.create_connection(url)
print("Connected to Coinbase WebSocket")

# Send subscription
ws.send(json.dumps(subscribe_msg))

# Stream data to Kafka
try:
    while True:
        time.sleep(1)
        result = ws.recv()
        result_json = json.loads(result)
        print("Sending to Kafka:", result_json)

        # Send to Kafka
        producer.produce(topic_name, json.dumps(result_json))
        producer.flush()
except KeyboardInterrupt:
    print("Interrupted")
    ws.close()
