from google.cloud import pubsub_v1
import time
import random
import json

project_id = "long-axle-412512"
topic_id = "example-window-pipeline"

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_id)

def generate_data():
    while True:
        data = {
            "timestamp": int(time.time()),
            "value": random.randint(1, 100)
        }
        message = json.dumps(data)
        publisher.publish(topic_path, message.encode("utf-8"))
        time.sleep(1)

if __name__ == "__main__":
    generate_data()
