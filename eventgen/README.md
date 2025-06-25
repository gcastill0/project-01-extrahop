# EventGen: Simulated HTTP/HTTPS Log Generator

This module provides a Python-based event generator for simulating realistic HTTP/HTTPS web traffic logs, including both legitimate and malicious request patterns.

## Features

- Simulates realistic web application traffic (GET, POST, PUT, DELETE, etc.)
- Generates structured log entries in JSON format
- Injects randomized malicious traffic patterns to test detection capabilities
- Supports log export to file for replay or SIEM ingestion

## Sample Output

Each log entry includes:

- Timestamps
- Protocol (HTTP/HTTPS)
- Client and server IPs
- URI and method
- Response status
- Round-trip time
- Headers
- User identifiers
- User-agent
- Malicious payloads (optional)

## Example Entry

```json
{
  "protocol": "HTTP",
  "time": 1724879342.692399,
  "client": {"ipaddr": "192.168.1.1"},
  "server": {"ipaddr": "203.0.113.10"},
  "method": "GET",
  "uri": "/api/data",
  "status_code": 200,
  "round_trip_time": 150,
  "request_header": {
    "Host": "example.com",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0"
  },
  "response_header": {
    "Content-Type": "application/json",
    "Content-Length": "1234"
  },
  "user_agent": "Mozilla/5.0",
  "response_content_type": "application/json",
  "user": "alice"
}
```
## Malicious Patterns

The malicious log entries are based on common attack patterns. Each record includes realistic fields like client, server, uri, method, status_code, and headers—targeting paths such as /admin, /wp-login.php, or exploits like ?cmd=rm -rf / or XSS.

 - Attack Type: Classifies the nature of the exploit (useful for tagging, alerting, or filtering).
 - Risk Level: Indicates the relative impact if the attack is successful.
 - URI Pattern: Can be used for detection rules or input sanitization guidance.

| URI Pattern                         | Description                                                                 | Attack Type             | Risk Level |
|-------------------------------------|-----------------------------------------------------------------------------|--------------------------|------------|
| `/admin`                            | Probing for unsecured admin portal.                                         | Unauthorized Access      | High       |
| `/wp-login.php`                     | Attempt to access WordPress login page—common brute-force target.          | Brute Force              | High       |
| `/api/user?id=1 OR 1=1`            | SQL injection attempting to bypass authentication or extract data.         | SQL Injection            | Critical   |
| `/index.php?page=../../etc/passwd` | Path traversal trying to read system password file on Unix systems.        | Directory Traversal      | High       |
| `/api/search?q=<script>alert(1)</script>` | XSS injection testing client-side script execution.                 | Cross-Site Scripting     | Medium     |
| `/cgi-bin/test.cgi?cmd=rm -rf /`   | Command injection attempting destructive server command.                   | Remote Code Execution    | Critical   |
| `/?id=1;DROP TABLE users`          | SQL injection that tries to delete a database table.                       | SQL Injection            | Critical   |
| `/phpmyadmin`                      | Scanning for phpMyAdmin—a known admin portal with vulnerabilities.         | Reconnaissance           | Medium     |
| `/api/data?user=admin'--`          | SQL injection using comment to ignore password clause.                     | SQL Injection            | High       |
| `/etc/shadow`                      | Attempt to access sensitive system file directly (Linux-based systems).    | Unauthorized File Access | High       |

