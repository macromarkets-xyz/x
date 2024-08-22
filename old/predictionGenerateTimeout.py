import json
import os
import argparse
import random
from datetime import datetime
import time 

def generate_prediction(timestamp, stock_ticker):
    prediction = {
        "timestamp": timestamp,
        "stock_ticker": stock_ticker,
        "prediction": random.random()  # Generates a random float between 0 and 1
    }
    
    # Ensure the directory exists
    os.makedirs("/tmp", exist_ok=True)
    
    # Write the prediction to the JSON file
    with open("/tmp/output.json", "w") as f:
        json.dump(prediction, f, indent=2)

def validate_iso8601(timestamp):
    try:
        datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return timestamp
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid ISO 8601 timestamp: {timestamp}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a prediction based on input parameters.")
    parser.add_argument("timestamp", type=validate_iso8601, help="Timestamp in ISO 8601 format")
    parser.add_argument("stock_ticker", type=str, help="Stock ticker symbol")
    
    args = parser.parse_args()
    
    time.sleep(3600)
    generate_prediction(args.timestamp, args.stock_ticker)
    print(f"Prediction generated and saved to /tmp/output.json")
    print(f"Timestamp: {args.timestamp}")
    print(f"Stock Ticker: {args.stock_ticker}")