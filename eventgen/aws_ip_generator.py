import ipaddress
import random

def generate_random_ip(network):
    """
    Generate a random IP address within the given network.
    
    Args:
        network (str): The IP network range in CIDR notation.
        
    Returns:
        str: A random IP address within the network.
    """
    net = ipaddress.ip_network(network)
    # Skip the first and last address to avoid network and broadcast addresses
    ip = net.network_address + random.randint(1, net.num_addresses - 2)
    return str(ip)

# AWS US East (N. Virginia) IP ranges
us_east_ranges = [
    "3.80.0.0/12",
    "3.90.0.0/15"
]

# AWS US West (Oregon) IP ranges
us_west_ranges = [
    "35.160.0.0/13",
    "52.32.0.0/14"
]

def simulate_ips_for_region(region_ranges, count=5):
    """
    Simulate a list of random IP addresses for a given AWS region.
    
    Args:
        region_ranges (list): List of IP ranges for the region.
        count (int): Number of IP addresses to generate.
        
    Returns:
        list: A list of random IP addresses.
    """
    ips = []
    for _ in range(count):
        # Randomly choose a network range
        selected_network = random.choice(region_ranges)
        # Generate a random IP within the selected range
        random_ip = generate_random_ip(selected_network)
        ips.append(random_ip)
    return ips
