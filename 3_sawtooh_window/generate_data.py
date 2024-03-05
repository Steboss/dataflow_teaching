import random
from datetime import datetime, timedelta
import ipaddress
from google.cloud import pubsub_v1
import time
import json
from structlog import get_logger


logger = get_logger()
project_id = "long-axle-412512"
topic_id = "example-sawtooth-window" # MODIFY THIS
# rojects/long-axle-412512/subscriptions/example-sawtooth-window-sub
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_id)


ipaddresses = [str(ip) for ip in ipaddress.IPv4Network('192.0.2.0/28')]
ipaddresses.extend([str(ip) for ip in ipaddress.IPv4Network('192.1.1.0/28')])
ipaddresses.extend([str(ip) for ip in ipaddress.IPv4Network('192.1.2.0/28')])
ipaddresses.extend([str(ip) for ip in ipaddress.IPv4Network('192.1.4.0/28')])
ipaddresses.extend([str(ip) for ip in ipaddress.IPv4Network('192.0.1.0/28')])


def generate_login_events(start_time, end_time, num_users=1000, num_scammers=10, event_rate_per_hour=10):
    users = [f'user_{i}' for i in range(num_users)]
    scammers = [f'scammer_{i}' for i in range(num_scammers)]
    events = []

    # Generate events for normal users
    for user in users:
        current_time = start_time
        while current_time < end_time:
            current_time += timedelta(hours=1/event_rate_per_hour)
            events.append({
                'timestamp': current_time,
                'user_id': user,
                'event_type': 'success' if random.random() < 0.95 else 'fail',  # 95% success rate
                'source_ip': random.choice(ipaddresses)
            })

    # Generate events for scammers
    for scammer in scammers:
        current_time = start_time
        while current_time < end_time:
            # Scammers try more frequently
            current_time += timedelta(minutes=random.randint(1, 30))
            events.append({
                'timestamp': current_time,
                'user_id': scammer,
                'event_type': 'fail',  # Scammers always fail
                'source_ip': '10.0.0.1'
            })

    return events


def publish_events():
    while True:
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=1)
        data = generate_login_events(start_time, end_time)
        for event in data:
            sender = random.uniform(0.1, 15) # generate a random number to send the event
            logger.info(f"Publishing {event} to {topic_path}")
            message = json.dumps(event)
            publisher.publish(topic_path, message.encode("utf-8"))
            time.sleep(sender)
# # Example usage
# start_time = datetime.now()
# end_time = start_time + timedelta(hours=1)  # Simulate over 1 hour
# events = generate_login_events(start_time, end_time)

publish_events()