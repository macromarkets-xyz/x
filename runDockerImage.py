import docker
import threading
import time
import os
import json
import tarfile
import io
from datetime import datetime, timedelta, timezone

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# This is now the same as SCRIPT_DIR, since the script is in the project root
PROJECT_DIR = SCRIPT_DIR

def run_docker_container(client, image_name, timeout, timestamp, stock_ticker):
    print(f"Running container with timestamp: {timestamp}, stock ticker: {stock_ticker}")
    
    # Define the path to the raw_price_data folder
    raw_price_data_path = os.path.join(PROJECT_DIR, 'raw_price_data')
    
    print(f"Looking for raw_price_data folder at: {raw_price_data_path}")
    # Ensure the raw_price_data folder exists
    if not os.path.exists(raw_price_data_path):
        raise FileNotFoundError(f"The raw_price_data folder does not exist at {raw_price_data_path}")
    
    container = client.containers.run(
        image_name,
        environment={
            "TIMESTAMP": timestamp,
            "STOCK_TICKER": stock_ticker
        },
        volumes={
            raw_price_data_path: {'bind': '/app/raw_price_data', 'mode': 'ro'}
        },
        detach=True
    )
    
    def stop_container():
        print(f"Timeout of {timeout} seconds reached. Stopping the container.")
        container.stop()
    
    timer = threading.Timer(timeout, stop_container)
    timer.start()
    
    try:
        for log in container.logs(stream=True):
            print(log.strip().decode())
    except docker.errors.NotFound:
        print("Container stopped due to timeout.")
    finally:
        timer.cancel()
        
    return container.id

def copy_file_from_container(client, container_id, src_path, dest_path):
    container = client.containers.get(container_id)
    bits, stat = container.get_archive(src_path)
    
    # Create a BytesIO object from the bits
    tar_data = io.BytesIO()
    for chunk in bits:
        tar_data.write(chunk)
    tar_data.seek(0)
    
    # Extract the file content from the tar archive
    with tarfile.open(fileobj=tar_data) as tar:
        file_content = tar.extractfile(os.path.basename(src_path)).read().decode('utf-8')
    
    # Write the content to the local file
    with open(dest_path, 'w') as f:
        f.write(file_content)
    
    print(f"File copied successfully to {dest_path}")
    print(f"Contents of {dest_path}:")
    print(file_content)
    
    return file_content

def run_fetch_stock_price(prediction_time, prediction_data):
    print(f"Waiting until {prediction_time} to fetch stock price...")
    wait_time = (datetime.fromisoformat(prediction_time.replace('Z', '+00:00')) - datetime.now(timezone.utc)).total_seconds()
    if wait_time > 0:
        time.sleep(wait_time)
    print("Starting fetchStockPrice.py...")
    import fetchStockPrice
    fetchStockPrice.main(prediction_time, prediction_data)

def main():
    image_name = "evaltest:v0"
    timeout = 120  # 2 minutes
    
    # Generate timestamp 5 minutes in the future in ISO 8601 format
    prediction_time = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat().replace('+00:00', 'Z')
    stock_ticker = "SPY"  # Default stock ticker
    
    client = docker.from_env()
    
    print(f"Running Docker container from image {image_name}")
    container_id = run_docker_container(client, image_name, timeout, prediction_time, stock_ticker)
    
    print("Copying output.json from container")
    output_path = os.path.join(SCRIPT_DIR, "output.json")
    file_content = copy_file_from_container(client, container_id, "/tmp/output.json", output_path)
    
    print("Cleaning up: Removing the container")
    client.containers.get(container_id).remove()

    # Read the prediction data
    try:
        prediction_data = json.loads(file_content)
        print("Successfully parsed prediction data:")
        print(json.dumps(prediction_data, indent=2))
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        print("File content:")
        print(file_content)
        return

    # Run fetchStockPrice.py
    run_fetch_stock_price(prediction_time, prediction_data)

if __name__ == "__main__":
    main()