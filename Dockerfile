# Use a base image with Python and nmap installed
FROM python:3.10-slim

# Install nmap and python-nmap
RUN apt-get update && apt-get install -y nmap && \
    pip install --no-cache-dir python-nmap && \
    #pip3 install --no-cache-dir python3-nmap && \
    rm -rf /var/lib/apt/lists/*

# Verify the installation of Nmap
RUN nmap --version

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . ./ 

# Command to run your Flask app
CMD ["gunicorn", "PortScanAPI:app", "--bind", "0.0.0.0:10000"]
CMD ["gunicorn", "webscrape:app", "--bind", "0.0.0.0:10000"]
#CMD ["gunicorn", "spiderProbe:app", "--bind", "0.0.0.0:10000"]
#CMD ["gunicorn", "directoryBF:app", "--bind", "0.0.0.0:10000"]
#CMD ["gunicorn", "subdomainBF:app", "--bind", "0.0.0.0:10000"]
