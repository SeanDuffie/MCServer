#General script by github.com/tushar2704, please adjust according to you requirements.

import psutil
import time
import logging

# Configure logging
logging.basicConfig(filename='system_monitor.log', level=logging.INFO,
                    format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Monitoring interval in seconds
interval = 60

while True:
    # Get CPU usage
    cpu_percent = psutil.cpu_percent()

    # Get memory usage
    memory = psutil.virtual_memory()
    memory_percent = memory.percent

    # Log the information
    logging.info(f"CPU Usage: {cpu_percent}%")
    logging.info(f"Memory Usage: {memory_percent}%")

    # Wait for the specified interval
    time.sleep(interval)
