import socket
import ssl
import requests
import ipaddress
import dns.resolver
import json
import os
from urllib.parse import urlparse

def resolve_public_ip(hostname, nameserver='8.8.8.8'):
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [nameserver]
    try:
        answer = resolver.resolve(hostname)
        ip = answer[0].to_text()
        print(f"[✓] External DNS resolution: {hostname} → {ip}")
        return ip
    except Exception as e:
        print(f"[✗] Failed external DNS resolution: {e}")
        return None

def is_public_ip(ip):
    """Return True if the IP address is publicly routable."""
    try:
        return ipaddress.ip_address(ip).is_global
    except ValueError:
        return False

def preflight_check(url, auth_token='', port=443):
    parsed = urlparse(url)
    hostname = parsed.hostname

    resolved_ip = resolve_public_ip(hostname)
    if not resolved_ip:
        return False

    if not is_public_ip(resolved_ip):
        print(f"[✗] Resolved IP {resolved_ip} is not public. VPN or DNS override may be active.")
        return False
    
    try:
        # Step 1: DNS resolution
        if not is_public_ip(resolved_ip):
            print(f"[✗] IP {resolved_ip} is not public. Possible VPN or proxy issue.")
            return False

        # Step 2: TLS Handshake Test
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        with socket.create_connection((resolved_ip, port), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                print(f"[✓] TLS handshake succeeded with {hostname}")
        
        # Step 3: HTTP GET test (use HEAD for minimal data)

        headers = {
            "Authorization": f"Bearer {auth_token}",
            'Content-Type': 'application/json'
        }

        r = requests.head(url, headers=headers, timeout=5, allow_redirects=True)

        # 401, 405 mean:
        # The server is real
        # The endpoint exists
        # But it doesn't allow the HEAD method — only POST (or maybe GET) is accepted

        if r.status_code in (200, 202, 204, 301, 302, 401, 405):
            print(f"[✓] HTTP request succeeded with status {r.status_code}")
            return True
        else:
            print(f"[✗] Unexpected HTTP status code: {r.status_code}")
            return False

    except Exception as e:
        print(f"[✗] Preflight check failed: {e}")
        return False

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

    auth_token  = os.getenv('AUTH_TOKEN')
    config.update({"auth_token": auth_token})

    return config

def main():
    config = load_config()
    if not preflight_check(
        url = config["webhook_url"], 
        auth_token = config["auth_token"]
    ):
        print("❌ Network conditions are not suitable. Exiting.")
        exit(1)

if __name__=="__main__":
    main()