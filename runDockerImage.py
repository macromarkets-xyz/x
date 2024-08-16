import docker
import subprocess
import threading
import time
import os
import sys
from datetime import datetime, timedelta, timezone

def run_docker_container(client, image_name, timeout, timestamp, stock_ticker):
    print(f"Running container with timestamp: {timestamp}, stock ticker: {stock_ticker}")
    container = client.containers.run(
        image_name,
        environment={
            "TIMESTAMP": timestamp,
            "STOCK_TICKER": stock_ticker
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

def copy_file_from_container(container_id, src_path, dest_path):
    cmd = f"docker cp {container_id}:{src_path} {dest_path}"
    result = subprocess.run(cmd, shell=True, check=True, text=True, capture_output=True)
    if result.returncode != 0:
        print(f"Error copying file: {result.stderr}")
    else:
        print(f"File copied successfully to {dest_path}")
    
    # Print the contents of the copied file
    with open(dest_path, 'r') as f:
        print(f"Contents of {dest_path}:")
        print(f.read())

def run_fetch_stock_price(prediction_time):
    print(f"Waiting until {prediction_time} to fetch stock price...")
    wait_time = (datetime.fromisoformat(prediction_time.replace('Z', '+00:00')) - datetime.now(timezone.utc)).total_seconds()
    if wait_time > 0:
        time.sleep(wait_time)
    print("Starting fetchStockPrice.py...")
    subprocess.run([sys.executable, "fetchStockPrice.py", prediction_time])

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
    copy_file_from_container(container_id, "/tmp/output.json", "./output.txt")
    
    print("Cleaning up: Removing the container")
    client.containers.get(container_id).remove()

    # Run fetchStockPrice.py
    run_fetch_stock_price(prediction_time)

if __name__ == "__main__":
    main()