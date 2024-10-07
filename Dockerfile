# Use a base image with Python and nmap installed
FROM python:3.10-slim

# Install nmap
RUN apt-get update && apt-get install -y nmap && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . ./

# Command to run your Flask app
CMD ["gunicorn", "PortScanAPI:app", "--bind", "0.0.0.0:10000"]
