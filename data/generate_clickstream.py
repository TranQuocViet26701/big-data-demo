#!/usr/bin/env python3
"""
Amazon Clickstream Data Generator
Generates synthetic clickstream data simulating user behavior on Amazon.com

Usage:
    python generate_clickstream.py [num_records]

Default: 10,000 records
"""

import csv
import random
import sys
from datetime import datetime, timedelta

# Configuration
PRODUCT_CATEGORIES = ['Electronics', 'Books', 'Clothing', 'Home', 'Sports',
                     'Toys', 'Beauty', 'Automotive', 'Garden', 'Food']

ACTIONS = ['view', 'click', 'add_to_cart', 'purchase']

# Action weights (view is most common, purchase is least common)
ACTION_WEIGHTS = [50, 30, 15, 5]

# Sample product names per category
PRODUCTS = {
    'Electronics': ['iPhone 14 Pro', 'Samsung TV 55"', 'Sony Headphones', 'iPad Air', 'Dell Laptop',
                   'Canon Camera', 'PlayStation 5', 'Apple Watch', 'Kindle Fire', 'Ring Doorbell'],
    'Books': ['Python Crash Course', 'Becoming', 'Atomic Habits', 'Harry Potter Set',
             'The Pragmatic Programmer', 'Clean Code', 'Sapiens', 'Educated', 'Dune', 'Project Hail Mary'],
    'Clothing': ['Nike Running Shoes', 'Levi\'s Jeans', 'North Face Jacket', 'Adidas T-Shirt',
                'Under Armour Hoodie', 'Puma Sneakers', 'Columbia Fleece', 'Tommy Hilfiger Shirt'],
    'Home': ['Dyson Vacuum', 'Instant Pot', 'Ninja Blender', 'KitchenAid Mixer',
            'Roomba Robot', 'Keurig Coffee Maker', 'Air Fryer', 'Memory Foam Pillow'],
    'Sports': ['Yoga Mat', 'Dumbbells Set', 'Running Belt', 'Resistance Bands',
              'Exercise Ball', 'Jump Rope', 'Foam Roller', 'Water Bottle'],
    'Toys': ['LEGO Star Wars', 'Barbie Dreamhouse', 'Hot Wheels Set', 'Nerf Gun',
            'Play-Doh Pack', 'Monopoly Board Game', 'Nintendo Switch', 'Action Figures'],
    'Beauty': ['Cetaphil Cleanser', 'CeraVe Moisturizer', 'Neutrogena Sunscreen',
              'Maybelline Mascara', 'Olay Regenerist', 'L\'Oreal Shampoo'],
    'Automotive': ['Michelin Tires', 'Car Phone Holder', 'Dash Cam', 'Jump Starter',
                  'Car Vacuum', 'Floor Mats', 'Air Freshener'],
    'Garden': ['Garden Hose', 'Pruning Shears', 'Plant Pots', 'Lawn Mower',
              'Seed Starter Kit', 'Garden Gloves', 'Watering Can'],
    'Food': ['Protein Bars', 'Organic Coffee', 'Granola Mix', 'Almond Butter',
            'Green Tea', 'Dark Chocolate', 'Pasta Set']
}


def generate_clickstream(num_records=10000, output_file='clickstream_large.txt'):
    """Generate synthetic clickstream data"""

    print(f"🔄 Generating {num_records:,} clickstream records...")

    # Start date: 30 days ago
    start_date = datetime.now() - timedelta(days=30)

    records = []

    for i in range(num_records):
        # Generate timestamp (random time in last 30 days)
        random_seconds = random.randint(0, 30 * 24 * 60 * 60)
        timestamp = start_date + timedelta(seconds=random_seconds)

        # Generate user_id (simulate 1000 unique users)
        user_id = f"user_{random.randint(1, 1000):04d}"

        # Select random category and product
        category = random.choice(PRODUCT_CATEGORIES)
        product = random.choice(PRODUCTS[category])
        product_id = f"{category[:3].upper()}_{abs(hash(product)) % 100000:05d}"

        # Select action based on weights
        action = random.choices(ACTIONS, weights=ACTION_WEIGHTS, k=1)[0]

        # Add some session information
        session_id = f"sess_{random.randint(1, 5000):05d}"

        # Create record
        record = {
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'user_id': user_id,
            'session_id': session_id,
            'product_id': product_id,
            'product_name': product,
            'category': category,
            'action': action,
            'price': round(random.uniform(9.99, 999.99), 2)
        }

        records.append(record)

        # Progress indicator
        if (i + 1) % 1000 == 0:
            print(f"  Generated {i + 1:,} records...")

    # Write to CSV file
    print(f"\n📝 Writing to {output_file}...")

    fieldnames = ['timestamp', 'user_id', 'session_id', 'product_id',
                 'product_name', 'category', 'action', 'price']

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    # Print statistics
    print(f"\n✅ Successfully generated {num_records:,} records!")
    print(f"📊 Statistics:")
    print(f"   - Unique users: ~1,000")
    print(f"   - Categories: {len(PRODUCT_CATEGORIES)}")
    print(f"   - Date range: {records[0]['timestamp']} to {records[-1]['timestamp']}")
    print(f"   - File: {output_file}")

    # Action distribution
    action_counts = {}
    for record in records:
        action_counts[record['action']] = action_counts.get(record['action'], 0) + 1

    print(f"\n📈 Action Distribution:")
    for action, count in sorted(action_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / num_records) * 100
        print(f"   - {action:15s}: {count:6,} ({percentage:5.2f}%)")

    # Category distribution
    category_counts = {}
    for record in records:
        category_counts[record['category']] = category_counts.get(record['category'], 0) + 1

    print(f"\n🏷️  Top 5 Categories:")
    for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        percentage = (count / num_records) * 100
        print(f"   - {category:15s}: {count:6,} ({percentage:5.2f}%)")


if __name__ == '__main__':
    # Get number of records from command line argument
    num_records = int(sys.argv[1]) if len(sys.argv) > 1 else 10000

    # Get output file name from command line argument
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'clickstream_large.txt'

    generate_clickstream(num_records, output_file)

    print(f"\n🎉 Data generation complete! Ready for HDFS upload.")
