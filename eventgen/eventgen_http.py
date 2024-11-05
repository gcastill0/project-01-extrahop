import json
import os
import requests
import random
import time
from datetime import datetime as dt, timezone
from aws_ip_generator import simulate_ips_for_region, us_east_ranges, us_west_ranges

# Load configuration from config.json
def load_config(file_path='config.json'):
    """
    Load the configuration from a JSON file.
    
    Args:
        file_path (str): Path to the JSON config file.
        
    Returns:
        dict: Configuration settings.
    """
    with open(file_path, 'r') as file:
        config = json.load(file)

    # Assume auth_token is an environment variable. Load it and 
    # then add it to the config. The token should not be written
    # in a file at any time.
    auth_token  = os.getenv('AUTH_TOKEN')
    config.update({"auth_token": auth_token})

    # Simulate IPs for US East and US West
    us_east_ips = simulate_ips_for_region(us_east_ranges)
    us_west_ips = simulate_ips_for_region(us_west_ranges)
    server_ips = us_east_ips + us_west_ips
    config.update({"server_ips": server_ips})

    return config

def generate_event(sample, config):
    event = sample.copy()

    # Real-time UTC date
    date = dt.now(timezone.utc)
    unix_time = date.timestamp()

    # Refactor data properties from event sample
    event["time"] = unix_time
    event["server"]["ipaddr"] = random.choice(config["server_ips"])
    
    # Check if the event is HTTP or HTTPS to capture transaction data
    # Create a dictionary with all relevant transaction data fields
    json_data = {
        # "timestamp": event["time"],                                        # Transaction timestamp in ISO format
        "protocol": "HTTP" if event["protocol"] == "HTTP" else "HTTPS",    # Determine the protocol
        "client_ip": str(event["client"]["ipaddr"]),                       # Client IP address
        "server_ip": str(event["server"]["ipaddr"]),                       # Server IP address
        "method": event["method"],                                         # HTTP method (GET, POST, etc.)
        "uri": event["uri"],                                               # URI accessed
        "response_code": event["status_code"],                             # HTTP response code
        "duration": event["round_trip_time"],                              # Transaction duration
        "request_headers": event["request_header"],                        # HTTP request headers
        "response_headers": event["response_header"],                      # HTTP response headers
        "user_agent": event["user_agent"],                                 # User agent string
        "content_type": event["response_content_type"]                     # Response content type
    }

    # Convert the dictionary to a JSON string
    final_event = json.dumps(json_data)

    # print(final_event)

    return final_event

def dispatch_event(event, config):
    # Send the JSON data to the webhook URL using an HTTP POST request

    # Define the webhook URL where the JSON data will be sent
    webhook_url = config["webhook_url"]
    
    # HTTPS request headers
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {config["auth_token"]}'
    }

    response = requests.post(webhook_url, headers=headers, data=event)

    # Check if the request was successful
    if response.status_code != 200:
      print(f"Failed to send data. Status code: {response.status_code}")

def parse_size(size_str):
    units = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3, "PB": 1024**4}
    size, unit = size_str[:-2], size_str[-2:]
    print("Looking for size: ", int(size) * units[unit])
    return int(size) * units[unit]

def parse_time_range(time_range):
    time_units = {'m': 60, 'h': 3600, 'd': 86400}
    
    # Extract the numeric part and the unit
    number = int(time_range[:-1])
    unit = time_range[-1]
    
    if unit not in time_units:
        raise ValueError("Invalid time unit. Use 'm' for minutes, 'h' for hours, or 'd' for days.")
    
    return number * time_units[unit]

def calculate_average_event_size(events):
    total_size = 0
    for event in events:
        # Convert event to JSON string and calculate its size in bytes
        event_str = json.dumps(event)
        event_size = len(event_str.encode('utf-8'))
        total_size += event_size
    
    average_size = total_size / len(events) if events else 0
    return average_size

def generate_events(config):
    # Use the sample events to rehydrate new events in the future
    f = open(config["samples"])
    events = json.load(f)

    byte_limit = parse_size(config['output_size'])
    total_time_seconds = parse_time_range(config["time_range"])

    average_event_size = calculate_average_event_size(events)
    estimated_events = byte_limit // average_event_size
    delay_per_event = total_time_seconds / estimated_events if estimated_events > 0 else 0

    # Timing measurement
    start_time = time.time()
    last_print_time = start_time
    elapsed_minutes = 0

    # Number of events
    event_count = 0

    # Loop control
    total_bytes = 0

    while total_bytes < byte_limit:
      sample = random.choice(events)
      event = generate_event(sample, config)
      dispatch_event(event, config)
      total_bytes += len(event.encode())
      event_count += 1
      time.sleep(delay_per_event)

      current_time = time.time()
      if current_time - last_print_time >= 60:
        elapsed_time = current_time - start_time
        elapsed_minutes = elapsed_time // 60
        print(f"Sent {event_count} events, {total_bytes} bytes in {int(elapsed_minutes)} minute(s).")
        last_print_time = current_time

    print(f"Sent {event_count} events, {total_bytes} bytes in {int(elapsed_minutes)} minute(s).")      

def main():
    config = load_config()
    generate_events(config)

if __name__=="__main__":
    main()
