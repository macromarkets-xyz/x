# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the Python script into the container
COPY predictionGenerate.py .

# Use environment variables to pass arguments
ENV TIMESTAMP=""
ENV STOCK_TICKER=""

# Run the script when the container launches
CMD python predictionGenerate.py "$TIMESTAMP" "$STOCK_TICKER"