# Use Python 3.10 as base image
FROM python:3.10

# Set working directory
WORKDIR /app

# Copy requirements and setup files
COPY requirements.txt .
COPY setup.py .

# Upgrade pip and install required Python packages
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Install Firefox and GeckoDriver for Selenium
RUN apt-get update && apt-get install -y firefox-esr
RUN wget -O /tmp/geckodriver.tar.gz https://github.com/mozilla/geckodriver/releases/download/v0.30.0/geckodriver-v0.30.0-linux64.tar.gz
RUN tar -C /usr/local/bin/ -zxvf /tmp/geckodriver.tar.gz
RUN chmod +x /usr/local/bin/geckodriver

# Create a profile for Selenium
RUN firefox -CreateProfile Selenium

# Copy the application code
COPY . .

# Initialize the databases
RUN python etl/databases/cassandra/setup_db.py
RUN python etl/databases/chroma/setup_db.py

# Set the command to run the application
CMD ["python", "app.py"]

# Expose the necessary port(s)
EXPOSE 28000
