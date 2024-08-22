import csv
from datetime import datetime, timedelta
import random

def generate_spy_data():
    start_date = datetime(2014, 1, 1)
    end_date = datetime.now()
    current_date = start_date
    current_price = 300.00  # Starting price

    data = []

    while current_date <= end_date:
        timestamp = current_date.strftime("%Y-%m-%d")
        
        # Generate new price with max 15% change
        max_change = current_price * 0.15
        price_change = random.uniform(-max_change, max_change)
        new_price = max(200, min(600, current_price + price_change))
        
        data.append([timestamp, f"{new_price:.2f}"])
        
        current_date += timedelta(days=1)
        current_price = new_price

    return data

def write_csv(filename, data):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['TIMESTAMP', 'PRICE'])  # Header
        writer.writerows(data)

# Generate and write data
spy_data = generate_spy_data()
write_csv('data_feed.csv', spy_data)

print(f"CSV file 'data_feed.csv' has been created with {len(spy_data)} rows of data.")