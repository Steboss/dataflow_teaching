import random
from datetime import datetime, timedelta

def generate_log_entry():
    timestamp = datetime(2022, 1, 1, 12, 0, 0) + timedelta(minutes=random.randint(0, 1440))
    event_type = f"event_type_{random.choice(['A', 'B', 'C'])}"
    duration = round(random.uniform(5.0, 30.0), 2)
    return f"{timestamp.isoformat()},{event_type},{duration}"

if __name__ == '__main__':
    output_file = 'log_entries_large.txt'

    with open(output_file, 'w') as file:
        for _ in range(10000000):
            file.write(generate_log_entry() + '\n')

    print(f"Generated log entries file: {output_file}")

