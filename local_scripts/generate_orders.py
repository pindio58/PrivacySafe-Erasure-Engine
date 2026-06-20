import csv
import random
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path

# Safely inject the project root directory into sys.path
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent  # Navigates up from 'scripts' to 'root'

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import logger
from project_utils.logger import get_logger

# Setup dynamic paths pointing to project_root/data/
DATA_DIR = PROJECT_ROOT / 'data'
USERS_FILE = DATA_DIR / 'users.csv'
OUTPUT_FILE = DATA_DIR / 'orders.csv'

# Constants
NUM_ORDERS = 20000
STATUSES = ['delivered', 'shipped', 'processing', 'cancelled', 'returned']
PAYMENTS = ['UPI', 'Card', 'NetBanking', 'COD', 'Wallet']
CITIES = [
    'Mumbai', 'Delhi', 'Bengaluru', 'Hyderabad', 'Chennai', 
    'Pune', 'Kolkata', 'Ahmedabad', 'Jaipur', 'Lucknow'
]

# Seed for reproducibility
random.seed(42)

def get_random_date() -> str:
    """Generates a random datetime string within the last 18 months."""
    days_ago = random.randint(0, 540)
    dt = datetime.now() - timedelta(days=days_ago)
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def load_user_ids(file_path: Path) -> list:
    """Reads user_ids from the existing users file."""
    if not file_path.exists():
        raise FileNotFoundError(
            f"Missing base users file at {file_path}. Run generate_users.py first!"
        )
        
    u_ids = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            u_ids.append(row['user_id'])
    return u_ids

def main():
    logger = get_logger(__name__)
    headers = [
        'order_id', 'user_id', 'order_date', 'order_status', 
        'payment_method', 'total_amount', 'shipping_city', 'created_at'
    ]
    
    # Ensure the data directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    try:
        user_ids = load_user_ids(USERS_FILE)
    except FileNotFoundError as e:
        logger.error(str(e))
        return

    # Write data to the orders CSV
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        
        for _ in range(NUM_ORDERS):
            order_date = get_random_date()
            total = round(random.uniform(299, 15999), 2)
            
            writer.writerow([
                str(uuid.uuid4()),
                random.choice(user_ids),
                order_date,
                random.choice(STATUSES),
                random.choice(PAYMENTS),
                total,
                random.choice(CITIES),
                order_date
            ])

    logger.info(f"Success! Created {NUM_ORDERS} orders at: {OUTPUT_FILE}")

if __name__ == '__main__':
    main()
