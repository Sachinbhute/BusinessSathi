#!/usr/bin/env python3
"""Generate sample retail transaction data for demo purposes."""

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

# Sample products and categories
PRODUCTS = [
    ("Coca Cola 500ml", "Beverages"),
    ("Lays Classic 50g", "Snacks"),
    ("Maggi 2-Minute Noodles", "Food"),
    ("Parle-G Biscuits 100g", "Snacks"),
    ("Tata Tea 250g", "Beverages"),
    ("Dettol Soap 100g", "Personal Care"),
    ("Colgate Toothpaste 100g", "Personal Care"),
    ("Rice 1kg", "Food"),
    ("Cooking Oil 1L", "Food"),
    ("Bread Loaf", "Food"),
    ("Milk 1L", "Dairy"),
    ("Eggs 12pcs", "Dairy"),
    ("Onions 1kg", "Vegetables"),
    ("Tomatoes 1kg", "Vegetables"),
    ("Potatoes 1kg", "Vegetables"),
]

PAYMENT_METHODS = ["Cash", "Card", "UPI", "Wallet"]

def generate_sample_data(num_days=7, transactions_per_day=20):
    """Generate sample transaction data."""
    data = []
    start_date = datetime.now() - timedelta(days=num_days-1)
    
    for day in range(num_days):
        current_date = start_date + timedelta(days=day)
        
        # More transactions on weekends
        if current_date.weekday() >= 5:  # Weekend
            num_transactions = int(transactions_per_day * 1.5)
        else:
            num_transactions = transactions_per_day
            
        for _ in range(num_transactions):
            product, category = random.choice(PRODUCTS)
            quantity = random.choices([1, 2, 3, 4, 5], weights=[50, 25, 15, 7, 3])[0]
            
            # Price ranges based on category
            if category == "Beverages":
                base_price = random.uniform(15, 50)
            elif category == "Snacks":
                base_price = random.uniform(10, 30)
            elif category == "Food":
                base_price = random.uniform(20, 150)
            elif category == "Personal Care":
                base_price = random.uniform(25, 100)
            elif category == "Dairy":
                base_price = random.uniform(30, 80)
            elif category == "Vegetables":
                base_price = random.uniform(15, 60)
            else:
                base_price = random.uniform(10, 100)
            
            unit_price = round(base_price, 2)
            discount = random.choices([0, 5, 10, 15], weights=[70, 20, 8, 2])[0]
            payment_method = random.choice(PAYMENT_METHODS)
            
            data.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "product": product,
                "category": category,
                "quantity": quantity,
                "unit_price": unit_price,
                "discount": discount,
                "payment_method": payment_method,
            })
    
    return data

def main():
    """Generate and save sample data."""
    # Create directories
    sample_dir = Path("sample_data")
    sample_dir.mkdir(exist_ok=True)
    
    # Generate data
    data = generate_sample_data()
    
    # Save to CSV
    csv_path = sample_dir / "shop_sample.csv"
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        if data:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
    
    print(f"Generated {len(data)} transactions in {csv_path}")
    
    # Generate additional demo scenarios
    scenarios = {
        "weekend_boost": generate_sample_data(num_days=3, transactions_per_day=35),
        "slow_week": generate_sample_data(num_days=5, transactions_per_day=8),
        "high_value": generate_sample_data(num_days=4, transactions_per_day=15)
    }
    
    for scenario_name, scenario_data in scenarios.items():
        scenario_path = sample_dir / f"demo_{scenario_name}.csv"
        with open(scenario_path, 'w', newline='', encoding='utf-8') as f:
            if scenario_data:
                writer = csv.DictWriter(f, fieldnames=scenario_data[0].keys())
                writer.writeheader()
                writer.writerows(scenario_data)
        print(f"Generated {len(scenario_data)} transactions in {scenario_path}")

if __name__ == "__main__":
    main()
