import json
from datetime import datetime, timezone
import sys
import subprocess
import time

def check_yfinance():
    try:
        import yfinance as yf
        return yf
    except ImportError:
        print("The 'yfinance' module is not installed. Would you like to install it now? (y/n)")
        choice = input().lower()
        if choice == 'y':
            subprocess.check_call([sys.executable, "-m", "pip", "install", "yfinance"])
            import yfinance as yf
            return yf
        else:
            print("Cannot proceed without yfinance. Exiting.")
            sys.exit(1)

def fetch_stock_price(yf, ticker):
    # Fetch stock data
    stock = yf.Ticker(ticker)
    
    # Get the latest available price
    latest_price = stock.history(period="1d")['Close'].iloc[-1]
    return latest_price

def calculate_percentage_difference(prediction, actual):
    return ((actual - prediction) / prediction) * 100

def main(prediction_time):
    yf = check_yfinance()

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
    actual_price = fetch_stock_price(yf, ticker)
    
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