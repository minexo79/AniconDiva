import csv
import random
from datetime import datetime, timedelta
import faker

NUM_ROWS = 10000 # Number of rows to generate

fake = faker.Faker()

def random_content():
    return fake.sentence(nb_words=random.randint(5, 15))

def generate_row(idx):
    # get fake name count
    _name = fake.user_name()
    if len(_name) > 16:
        _name = _name[:16]

    return [
        idx,
        _name,
        random_content(),
        (datetime.now() - timedelta(minutes=random.randint(0, 10000))).isoformat(sep=' ', timespec='seconds'),
        fake.ipv4(),
        fake.user_agent(),
        random.choice(["pending", "approved", "rejected"])
    ]

# Output file name
filename = "sample_data.csv"

# Header
header = ["ID", "Nickname", "Content", "Timestamp", "IP", "User-Agent", "Status"]

with open(filename, mode='w', encoding='utf-8', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(header)

    for i in range(1, NUM_ROWS+1):
        writer.writerow(generate_row(i))

print(f"CSV file '{filename}' created with {NUM_ROWS} rows.")
