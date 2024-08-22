import json
from datetime import datetime, timezone
import time
import requests

def fetch_stock_price(ticker, api_key):
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
        raise ValueError("Error fetching data or invalid response from Alpha Vantage.")

def calculate_percentage_difference(prediction, actual):
    return ((actual - prediction) / prediction) * 100

def main(prediction_time, prediction_data):
    ticker = prediction_data['stock_ticker']
    prediction = prediction_data['prediction']
    
    # Wait until the prediction time
    wait_time = (datetime.fromisoformat(prediction_time.replace('Z', '+00:00')) - datetime.now(timezone.utc)).total_seconds()
    if wait_time > 0:
        print(f"Waiting {wait_time:.2f} seconds until {prediction_time}...")
        time.sleep(wait_time)
    
    # Fetch the stock price
    api_key = 'SRRBBG5N94HXD80A'  # Replace with your actual Alpha Vantage API key
    try:
        actual_price = fetch_stock_price(ticker, api_key)
    except ValueError as e:
        print(f"Error: {e}")
        return
    
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
    import sys
    if len(sys.argv) != 3:
        print("Usage: python fetchStockPrice.py <prediction_time> <prediction_data_json>")
        sys.exit(1)
    prediction_time = sys.argv[1]
    prediction_data = json.loads(sys.argv[2])
    main(prediction_time, prediction_data)