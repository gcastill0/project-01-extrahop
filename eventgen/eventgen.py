import json
import os
import requests
import random
import time
import math
from datetime import datetime as dt, timezone, timedelta
from aws_ip_generator import simulate_ips_for_region, us_east_ranges, us_west_ranges
from samplegen import getMaliciousEntry, getBeningEntries
from preflight import preflight_check

# Simulate a public IP Address
def get_public_ip():
    # Avoid private/reserved IP ranges (basic version)
    while True:
        ip = ".".join(str(random.randint(1, 254)) for _ in range(4))
        if not ip.startswith(("10.", "172.", "192.", "127.")):  # skip private/reserved ranges
            return ip
        else:
            return None

# Rare IP address by very random chance
def maybe_generate_public_ip(chance=0.001):
    # 0.001 = 0.1% chance
    if random.random() < chance:
        return get_public_ip()
    else:
        return None

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

def generate_event_template():
    event_template = {
      "event" : {               
        "message": "Message",
        "severity": "INFO"
      },
      "time" : 1,  
      "host": "D6T6RGQQ4T",    
      "source" : "Python Generator",  
      "sourcetype" : "",   
      "index": "",        
      "fields" : { }       
    }
    return event_template

def generate_event(sample, config):
    event_template = generate_event_template()
    event = sample.copy()

    # Real-time UTC date
    date = dt.now(timezone.utc)
    unix_time = date.timestamp()

    # Get random IP address
    client_public_ip = maybe_generate_public_ip()

    # Format for the /event endpoint
    event_template["event"]["message"] = event["message"]
    event_template["event"]["severity"] = event["severity"]

    # Refactor data properties from event sample
    event_template["time"] = unix_time
    event_template["sourcetype"] = "Extrahop"

    event["server"]["ipaddr"] = random.choice(config["server_ips"])
    event["round_trip_time"]  = random.randint(20, 500)
    
    # Check if the event is HTTP or HTTPS to capture transaction data
    # Create a dictionary with all relevant transaction data fields
    json_data = {
        # "timestamp": event["time"],                                      # Transaction timestamp in ISO format
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
        "content_type": event["response_content_type"],                    # Response content type
        "user": event["user"]                                              # User
    }

    event_template["fields"] = json_data

    # Update with rare remote IP
    # if event["user"] == 'alice' and client_public_ip is not None: 
    #     json_data["client_ip"] = str(client_public_ip)

    # Convert the dictionary to a JSON string
    # final_event = json.dumps(json_data)
    final_event = event_template

    # print(final_event)

    return final_event

def dispatch_event(events, config):
    # Send the JSON data to the webhook URL using an HTTP POST request

    # Define the webhook URL where the JSON data will be sent
    webhook_url = config["webhook_url"]
    
    # HTTPS request headers
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {config["auth_token"]}'
    }

    # for event in events:
    #     print(event, "\n\n")

    payload = "\n".join(json.dumps(event) for event in events)    
    response = requests.post(webhook_url, headers=headers, data=payload)

    # Check if the request was successful
    if response.status_code != 200:
      print(f"Failed to send data. Status code: {response.status_code}")

def parse_size(size_str):
    units = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3, "PB": 1024**4}
    size, unit = size_str[:-2], size_str[-2:]
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

def generate_events_linear(config):
    # Use the sample events to rehydrate new events in the future
    # f = open(config["samples"])
    events = getBeningEntries()

    byte_limit = parse_size(config['output_size'])
    total_time_seconds = parse_time_range(config["time_range"])
    average_event_size = math.ceil(calculate_average_event_size(events))
    estimated_events = round(byte_limit / average_event_size)
    delay_per_event = (total_time_seconds / estimated_events) * 0.75 if estimated_events > 0 else 0

    # Timing measurement
    start_time = time.time()
    last_print_time = start_time
    elapsed_minutes = 0
    elapsed_time = 0
    elapsed_loop_time = 0

    # Calculate a random delay within the first 10 minutes
    jitter_minutes = random.randint(0, 9)
    jitter_seconds = random.randint(0, 59)
    attack_delay = jitter_minutes * 60 + jitter_seconds
    attack_time = dt.now(timezone.utc) + timedelta(seconds=attack_delay)

    # Number of events
    event_count = 0

    # Loop control
    total_bytes = 0

    event_bundle = []

    while event_count < estimated_events:
      current_time = time.time()
      sample = random.choice(events)
    
      event = generate_event(sample, config)

      if dt.now(timezone.utc) > attack_time:
          event = generate_event(getMaliciousEntry(), config)
          # Calculate a random delay within the next 40 minutes to 1 hour
          jitter_minutes = random.randint(40, 59) * 60
          jitter_seconds = random.randint(0, 59)
          attack_delay = jitter_minutes * 60 + jitter_seconds
          attack_time = dt.now(timezone.utc) + timedelta(seconds=attack_delay)

      event_bundle.append(event)
      total_bytes += len(event)
      event_count += 1
      elapsed_time += elapsed_loop_time

      if elapsed_time >= 1 or event_count == estimated_events:
        dispatch_event(event_bundle, config)
        event_bundle = []
        elapsed_time = 0

      if current_time - last_print_time >= 60 or event_count == estimated_events:
        elapsed_time = current_time - start_time
        elapsed_minutes = elapsed_time // 60
        print(f"{event_count:,.6g} events out of {estimated_events:,.6g} -- {((event_count/estimated_events)*100):.2f} % in {int(elapsed_minutes)} minute(s).")
        last_print_time = current_time

      time.sleep(delay_per_event)
      end_time = time.time()
      elapsed_loop_time = end_time - current_time

def generate_events_wave(config):
    # Load samples
    events = getBeningEntries()

    # Config parameters
    byte_limit = parse_size(config['output_size'])
    total_time_seconds = parse_time_range(config["time_range"])
    average_event_size = math.ceil(calculate_average_event_size(events))
    estimated_events = round(byte_limit / average_event_size)
    total_minutes = math.ceil(total_time_seconds / 60)

    # Build sine multipliers over 2 full periods
    multipliers = []
    for i in range(total_minutes):
        radians = (2 * math.pi * 2 * i) / total_minutes  # 2 full sine wave periods
        value = (math.sin(radians) + 1) / 2              # Normalize to 0–1
        scaled = 0.2 + (value * 0.8)                     # Scale to 0.2–1.0
        multipliers.append(scaled)

    # Normalize multipliers to match total event count
    multiplier_sum = sum(multipliers)
    normalized_multipliers = [m / multiplier_sum for m in multipliers]
    events_per_minute = [round(estimated_events * m) for m in normalized_multipliers]

    print("Total estimated events:", estimated_events)
    print("Distribution per minute (sample):", events_per_minute[:10], "...")

    event_count = 0
    total_bytes = 0
    start_time = time.time()
    last_print_time = start_time

    # First malicious attack scheduling
    jitter_seconds = random.randint(300, 599) # Between 5–10 min
    attack_time = dt.now(timezone.utc) + timedelta(seconds=jitter_seconds)

    for minute_index, event_count_this_minute in enumerate(events_per_minute):
        bundle = []
        minute_start_time = time.time()
        delay_between_events = 60 / event_count_this_minute if event_count_this_minute > 0 else 0

        for _ in range(event_count_this_minute):
            now = dt.now(timezone.utc)

            if now > attack_time:
                sample = getMaliciousEntry()
                # Schedule next malicious attack
                jitter_seconds = random.randint(2400, 3599)  # Between 40–60 min
                attack_time = now + timedelta(seconds=jitter_seconds)
            else:
                sample = random.choice(events)

            event = generate_event(sample, config)
            bundle.append(event)
            total_bytes += len(json.dumps(event).encode("utf-8"))
            event_count += 1

            if delay_between_events > 0:
                time.sleep(delay_between_events)

        dispatch_event(bundle, config)

        # Logging
        now = time.time()
        if now - last_print_time > 60:
            elapsed_minutes = (now - start_time) / 60
            pct = (event_count / estimated_events) * 100
            print(f"{event_count:,.6g} events out of {estimated_events:,.6g} -- {pct:.2f}% in {int(elapsed_minutes)} minute(s).")
            last_print_time = now

    # Final log
    total_elapsed = time.time() - start_time
    print(f"Completed: {event_count:,} events in {total_elapsed:.2f} seconds ({total_elapsed/60:.2f} minutes)")

def main():
    config = load_config()

    if not preflight_check(
        url = config["webhook_url"], 
        auth_token = config["auth_token"]
    ):
        print("❌ Network conditions are not suitable. Exiting.")
        exit(1)
        
    # generate_events_linear(config)
    generate_events_wave(config)

if __name__=="__main__":
    main()
