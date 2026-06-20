import csv
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from faker import Faker

# Safely inject the project root directory into sys.path
import sys
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent  # Navigates up from 'scripts' to 'root'

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import logger (Ensure folder name matches exactly: project_utils vs project_utls)
from project_utils.logger import get_logger

# Setup dynamic data path: targets project_root/data/users.csv
DATA_DIR = PROJECT_ROOT / 'data'
OUTPUT_FILE = DATA_DIR / 'users.csv'

# Initialize Faker with seed for reproducibility
fake = Faker('en_IN')
Faker.seed(42)
random.seed(42)

NUM_USERS = 5000

def get_random_created_at() -> str:
    """Generates a random datetime string within the last 18 months."""
    days_ago = random.randint(0, 540)
    dt = datetime.now() - timedelta(days=days_ago)
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def generate_user_data(fake_generator: Faker) -> list:
    """Generates a structured mock user record."""
    first = fake_generator.first_name()
    last = fake_generator.last_name()
    user_id = str(uuid.uuid4())
    
    # Sanitise names for clean emails (removes spaces, dots, and apostrophes)
    clean_first = "".join(c for c in first.lower() if c.isalnum())
    clean_last = "".join(c for c in last.lower() if c.isalnum())
    email = f"{clean_first}.{clean_last}{random.randint(10, 999)}@example.com"
    
    return [
        user_id,
        first,
        last,
        email,
        fake_generator.phone_number(),
        fake_generator.street_address().replace('\n', ', '),  # Prevents broken CSV rows
        fake_generator.city(),
        fake_generator.state(),
        fake_generator.postcode(),
        'India',
        get_random_created_at(),
        ''  # deleted_at = NULL
    ]

def main():
    logger = get_logger(__name__)
    headers = [
        'user_id', 'first_name', 'last_name', 'email', 'phone',
        'address_line1', 'city', 'state', 'pincode', 'country',
        'created_at', 'deleted_at'
    ]
    
    # Safely create the data folder inside project root if it does not exist
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Write data to the CSV
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        
        for _ in range(NUM_USERS):
            writer.writerow(generate_user_data(fake))

    logger.info(f"Success! Created {NUM_USERS} users at: {OUTPUT_FILE}")

if __name__ == '__main__':
    main()
