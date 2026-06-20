# generate_products.py
import csv
import random
import sys
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
OUTPUT_FILE = DATA_DIR / 'products.csv'

# Seed for reproducibility
random.seed(42)

def main():
    logger = get_logger(__name__)
    headers = ['product_id', 'product_name', 'category', 'brand', 'price']
    
    categories = {
        'Electronics': ['boAt', 'Samsung', 'Xiaomi', 'Realme', 'OnePlus'],
        'Fashion': ["Levi's", 'Nike', 'Adidas', 'Zara', 'H&M'],
        'Home': ['IKEA', 'Prestige', 'Philips', 'Havells', 'Borosil'],
        'Beauty': ['Lakme', 'Maybelline', 'Mamaearth', 'Nivea', 'Plum'],
        'Books': ['Penguin', 'HarperCollins', 'Rupa', 'Westland', 'Jaico']
    }

    products = []
    product_id = 1001

    # Generate synthetic products structure
    for category, brands in categories.items():
        for i in range(10):  # 10 products per category = 50 total
            brand = random.choice(brands)
            name = f"{brand} {category} Model {i+1}"
            price = round(random.uniform(199, 24999), 2)
            
            products.append([product_id, name, category, brand, price])
            product_id += 1

    # Ensure the target data directory exists before writing
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Write data to products CSV
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(products)

    logger.info(f"Success! Created {len(products)} products at: {OUTPUT_FILE}")

if __name__ == '__main__':
    main()
