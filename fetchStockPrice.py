import json
from datetime import datetime, timezone
import sys
import subprocess
import time
import requests

def check_requests():
    try:
        import requests
        return requests
    except ImportError:
        print("The 'requests' module is not installed. Would you like to install it now? (y/n)")
        choice = input().lower()
        if choice == 'y':
            subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
            import requests
            return requests
        else:
            print("Cannot proceed without requests. Exiting.")
            sys.exit(1)

def fetch_stock_price(requests, ticker, api_key):
    base_url = 'https://www.alphavantage.co/query'
    function = 'GLOBAL_QUOTE'
    
    params = {
        'function': function,
        'symbol': ticker,
        'apikey': api_key
    }
    
    response = requests.get(base_url, params=params)
    data = response.json()
    
    if 'Global Quote' in data and '05. price' in data['Global Quote']:
        return float(data['Global Quote']['05. price'])
    else:
        print("Error fetching data or invalid response from Alpha Vantage.")
        sys.exit(1)

def calculate_percentage_difference(prediction, actual):
    return ((actual - prediction) / prediction) * 100

def main(prediction_time):
    requests = check_requests()

    # Read the existing output.txt file
    with open('output.txt', 'r') as f:
        prediction_data = json.load(f)
    
    ticker = prediction_data['stock_ticker']
    prediction = prediction_data['prediction']
    
    # Wait until the prediction time
    wait_time = (datetime.fromisoformat(prediction_time.replace('Z', '+00:00')) - datetime.now(timezone.utc)).total_seconds()
    if wait_time > 0:
        print(f"Waiting {wait_time:.2f} seconds until {prediction_time}...")
        time.sleep(wait_time)
    
    # Fetch the stock price
    api_key = 'SRRBBG5N94HXD80A'  # Replace with your actual Alpha Vantage API key
    actual_price = fetch_stock_price(requests, ticker, api_key)
    
    # Get the current time after fetching the price
    fetch_time = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    
    # Calculate the percentage difference
    percent_difference = calculate_percentage_difference(prediction, actual_price)
    
    # Create results.txt with the comparison
    results = {
        'stock_ticker': ticker,
        'prediction_time': prediction_time,
        'predicted_value': prediction,
        'actual_value': actual_price,
        'fetch_time': fetch_time,
        'percent_difference': percent_difference
    }
    
    with open('results.txt', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Created results.txt with comparison data for {ticker}")
    print(f"Predicted value: {prediction}")
    print(f"Actual price: {actual_price}")
    print(f"Percent difference: {percent_difference:.2f}%")
    print(f"Fetch time: {fetch_time}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python fetchStockPrice.py <prediction_time>")
        sys.exit(1)
    main(sys.argv[1])