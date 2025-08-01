import csv
import random
from datetime import datetime, timedelta
import faker

NUM_ROWS = 500 # Number of rows to generate

fake = faker.Faker()

def random_content():
    return fake.sentence(nb_words=random.randint(15, 100))

def generate_row(idx) -> list:
    # get fake name count
    _name = fake.user_name()
    if len(_name) > 16:
        _name = _name[:16]

    return [
        idx,
        _name,
        random_content(),
        fake.ipv4(),
        fake.chrome(),
        1,  # Default tag
        random.choice([1, 2, 3, 4]),
        (datetime.now() - timedelta(minutes=random.randint(0, int(NUM_ROWS)))).isoformat(sep=' ', timespec='seconds')
    ]


def generate_csv():
    """Generate a CSV file with fake data."""
    # Output file name
    filename = "sample_data.csv"

    # Header
    header = ["ID", "Nickname", "Content", "IP", "User-Agent", "Tag", "status", "Timestamp"]

    with open(filename, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)

        for i in range(1, NUM_ROWS+1):
            writer.writerow(generate_row(i))

    print(f"CSV file '{filename}' created with {NUM_ROWS} rows.")
