# Use Python 3.10 as base image
FROM python:3.10

# Set working directory
WORKDIR /app

# Copy requirements and setup files
COPY requirements.txt .
COPY setup.py .

# Upgrade pip and install required Python packages
RUN pip install --upgrade pip
## This approach uses cache to save each package installation
## so no need to restart pip install every time it fails during 
## initial build
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt 

# Install GeckoDriver for Selenium
RUN wget -O /tmp/geckodriver.tar.gz https://github.com/mozilla/geckodriver/releases/download/v0.30.0/geckodriver-v0.30.0-linux64.tar.gz
RUN tar -C /usr/local/bin/ -zxvf /tmp/geckodriver.tar.gz
RUN chmod +x /usr/local/bin/geckodriver

# Install Firefox
RUN apt-get update && apt-get install -y firefox-esr

# Create a profile for Selenium
RUN firefox -CreateProfile Selenium -headless

# Add cron and cron job file
RUN apt-get update && apt-get install -y cron
COPY cronjob /etc/cron.d/cronjob
RUN chmod 0644 /etc/cron.d/cronjob
RUN crontab /etc/cron.d/cronjob
RUN touch /var/log/cron.log

# Copy the application code
COPY . .

# Set the command to run the application
CMD service cron start && python app.py

# Expose the necessary port(s)
EXPOSE 28000
