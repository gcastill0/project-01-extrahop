import random
import time
import json
from faker import Faker
import ipaddress
from functools import lru_cache

fake = Faker()

# Define malicious patterns
malicious_patterns = [
    ("/admin", "GET", 401, 2, "Probing for unsecured admin portal."),
    ("/wp-login.php", "POST", 403, 3, "Login page common brute-force target."),
    ("/login", "POST", 401, 2, "Attempt to access generic login page."),
    ("/etc/passwd", "GET", 404, 3, "Unix password file enumeration attempt."),
    ("/index.php?user=admin'--", "GET", 403, 4, "SQL injection using comment truncation."),
    ("/search?q=<script>alert(1)</script>", "GET", 400, 4, "Cross-site scripting (XSS) injection test."),
    ("/api/delete/../../etc/passwd", "DELETE", 403, 4, "Path traversal attempt to access restricted files."),
    ("/api/user?id=1 OR 1=1", 5, 403, "HIGH", "SQL injection bypass attempt using logical tautology."),
    ("/api/upload", "POST", 405, 5, "Upload attempt to disabled or unpermitted endpoint."),
    ("/.git/config", "GET", 404, 4, "Reconnaissance for exposed version control metadata."),
    ("/?cmd=rm+-rf+/", "GET", 400, 5, "Command injection probing for remote shell execution."),
]

# Define CIDRs for high-risk countries
high_risk_cidrs = [
    '5.8.0.0/16',         # Russia
    '91.200.12.0/22',     # Russia
    '36.96.0.0/12',       # China
    '42.80.0.0/14',       # China
    '175.45.176.0/22',    # North Korea
    '37.98.128.0/17',     # Iran
    '185.112.0.0/22',     # Iran
    '93.125.0.0/18',      # Belarus
    '178.172.0.0/15'      # Belarus
]

def get_biased_malicious_ip():
    return random_ip_from_cidr(random.choice(high_risk_cidrs))

def random_ip_from_cidr(cidr):
    net = ipaddress.IPv4Network(cidr)
    # Skip network and broadcast addresses
    return str(random.choice(list(net.hosts())))

@lru_cache(maxsize=None)
def generate_ip_pool(size=100, include_ipv6=False):
    """
    Generate a pool of IP addresses using Faker.
    
    :param size: Number of IP addresses to generate (default 100).
    :param include_ipv6: Whether to include IPv6 addresses in the pool (default False).
    :return: List of IP addresses.
    """
    fake = Faker()
    if include_ipv6:
        return [fake.ipv4() if i % 2 == 0 else fake.ipv6() for i in range(size)]
    else:
        return [fake.ipv4() for _ in range(size)]

# Function to generate a single log entry (malicious or benign)
def generate_log_entry(malicious=False, pattern = {}):
    if malicious:
        uri, method, status, severity, message = pattern
        client_ip = get_biased_malicious_ip()

    else:
        uri = "/" + fake.uri_path()
        method = random.choice(["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD"])
        status = random.choice([200, 201, 202, 204, 206, 301, 302, 303, 304, 307, 308, 408, 429, 500, 501, 502, 503, 504])
        client_ip = random.choice(generate_ip_pool())
        severity = 1
        message = "Common incoming request."
        
    return {
        "message": message,
        "severity": severity,
        "time": round(time.time(), 6),
        "protocol": random.choice(["HTTP", "HTTPS"]),
        "client": {"ipaddr": client_ip},
        "server": {"ipaddr": fake.ipv4_public()},
        "method": method,
        "uri": uri,
        "status_code": status,
        "round_trip_time": random.randint(50, 500),
        "request_header": {
            "Host": fake.hostname(),
            "User-Agent": fake.user_agent(),
            "Content-Type": random.choice(["application/json", "application/x-www-form-urlencoded", "multipart/form-data"])
        },
        "response_header": {
            "Content-Type": "application/json",
            "Content-Length": str(random.randint(0, 10000))
        },
        "response_content_type": "application/json",
        "user": fake.user_name()
    }

def getMaliciousEntry():
    return generate_log_entry(malicious=True, pattern=random.choice(malicious_patterns))

def getBeningEntries(max = 1000):
    log_entries = [generate_log_entry(malicious=False) for _ in range(max)]
    random.shuffle(log_entries)
    return log_entries


def main():
    print(getMaliciousEntry())
    print(getBeningEntries(1)[0])

if __name__=="__main__":
    main()