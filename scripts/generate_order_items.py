# generate_order_items.py
import csv
import random
import sys
import uuid
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
ORDERS_FILE = DATA_DIR / 'orders.csv'
PRODUCTS_FILE = DATA_DIR / 'products.csv'
OUTPUT_FILE = DATA_DIR / 'order_items.csv'

# Seed for reproducibility
random.seed(42)

def load_products(file_path: Path) -> list:
    """Reads product data containing product_id and price from the CSV file."""
    if not file_path.exists():
        raise FileNotFoundError(f"Missing base products file at {file_path}.")
        
    prods = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            prods.append({
                'product_id': row['product_id'],
                'price': float(row['price'])
            })
    return prods

def load_order_ids(file_path: Path) -> list:
    """Reads order_ids from the existing orders CSV file."""
    if not file_path.exists():
        raise FileNotFoundError(f"Missing base orders file at {file_path}. Run generate_orders.py first!")
        
    o_ids = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            o_ids.append(row['order_id'])
    return o_ids

def main():
    logger = get_logger(__name__)
    headers = ['order_item_id', 'order_id', 'product_id', 'quantity', 'unit_price', 'line_total']
    
    # Ensure the data directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Safely load the dependencies
    try:
        products = load_products(PRODUCTS_FILE)
        order_ids = load_order_ids(ORDERS_FILE)
    except FileNotFoundError as e:
        logger.error(str(e))
        return
    except ValueError as e:
        logger.error(f"Data formatting error in input files: {e}")
        return

    total_items_created = 0

    # Write data to the order items CSV
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)

        for order_id in order_ids:
            # 1 to 4 items per order using weighted probabilities
            num_items = random.choices([1, 2, 3, 4], weights=[40, 35, 20, 5])[0]
            
            # Avoid sampling errors if products list is shorter than the requested items
            sample_size = min(num_items, len(products))
            chosen_products = random.sample(products, sample_size)

            for prod in chosen_products:
                qty = random.randint(1, 3)
                unit_price = prod['price']
                line_total = round(qty * unit_price, 2)

                writer.writerow([
                    str(uuid.uuid4()),
                    order_id,
                    prod['product_id'],
                    qty,
                    unit_price,
                    line_total
                ])
                total_items_created += 1

    logger.info(f"Success! Created {total_items_created} order items line records at: {OUTPUT_FILE}")

if __name__ == '__main__':
    main()
