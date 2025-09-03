#!/usr/bin/env python3
"""
Security Scanner for Retail Management System
External security scanning and vulnerability assessment
"""

import os
import sys
import subprocess
import json
import requests
from datetime import datetime
from urllib.parse import urljoin, urlparse
import socket
import ssl

class SecurityScanner:
    """
    Comprehensive security scanner for external vulnerability assessment
    """

    def __init__(self, target_url, target_host=None, target_port=80):
        """
        Initialize security scanner

        Args:
            target_url (str): Target URL to scan
            target_host (str): Target host/IP (optional)
            target_port (int): Target port (default: 80)
        """
        self.target_url = target_url
        self.target_host = target_host or urlparse(target_url).hostname
        self.target_port = target_port
        self.results = {}
        self.scan_start_time = None
        self.scan_end_time = None

    def start_scan(self):
        """Start comprehensive security scan"""
        print("🔍 Starting Security Scan...")
        print(f"Target: {self.target_url}")
        print(f"Host: {self.target_host}")
        print(f"Port: {self.target_port}")
        print("=" * 60)

        self.scan_start_time = datetime.now()

        # Run all security scans
        self.run_port_scan()
        self.run_ssl_scan()
        self.run_web_vulnerability_scan()
        self.run_header_security_check()
        self.run_directory_enumeration()
        self.run_sql_injection_scan()
        self.run_xss_scan()

        self.scan_end_time = datetime.now()
        self.generate_report()

    def run_port_scan(self):
        """Run basic port scanning"""
        print("📡 Running Port Scan...")

        try:
            # Check common ports
            common_ports = [80, 443, 22, 21, 25, 53, 110, 143, 993, 995]
            open_ports = []

            for port in common_ports:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    result = sock.connect_ex((self.target_host, port))
                    if result == 0:
                        open_ports.append(port)
                    sock.close()
                except:
                    continue

            self.results['port_scan'] = {
                'open_ports': open_ports,
                'total_checked': len(common_ports),
                'status': 'completed'
            }

            print(f"✅ Found {len(open_ports)} open ports: {open_ports}")

        except Exception as e:
            self.results['port_scan'] = {
                'error': str(e),
                'status': 'failed'
            }
            print(f"❌ Port scan failed: {str(e)}")

    def run_ssl_scan(self):
        """Run SSL/TLS security scan"""
        print("🔒 Running SSL/TLS Scan...")

        try:
            # Check if HTTPS is available
            https_url = self.target_url.replace('http://', 'https://')

            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            with socket.create_connection((self.target_host, 443)) as sock:
                with context.wrap_socket(sock, server_hostname=self.target_host) as ssock:
                    cert = ssock.getpeercert()
                    cipher = ssock.cipher()

                    ssl_info = {
                        'certificate': {
                            'subject': dict(x[0] for x in cert.get('subject', [])),
                            'issuer': dict(x[0] for x in cert.get('issuer', [])),
                            'version': cert.get('version'),
                            'serial_number': str(cert.get('serialNumber')),
                            'not_before': cert.get('notBefore'),
                            'not_after': cert.get('notAfter'),
                        },
                        'cipher': {
                            'name': cipher[0],
                            'protocol': cipher[1],
                            'bits': cipher[2]
                        },
                        'tls_version': ssock.version(),
                        'status': 'completed'
                    }

                    self.results['ssl_scan'] = ssl_info
                    print("✅ SSL/TLS scan completed")

        except Exception as e:
            self.results['ssl_scan'] = {
                'error': str(e),
                'status': 'failed'
            }
            print(f"❌ SSL scan failed: {str(e)}")

    def run_web_vulnerability_scan(self):
        """Run basic web vulnerability scan"""
        print("🌐 Running Web Vulnerability Scan...")

        vulnerabilities = []

        try:
            # Test for common vulnerabilities
            test_cases = [
                {
                    'name': 'Directory Listing',
                    'url': '/backup/',
                    'check': lambda r: 'index of' in r.text.lower()
                },
                {
                    'name': 'PHP Info Disclosure',
                    'url': '/phpinfo.php',
                    'check': lambda r: 'php version' in r.text.lower()
                },
                {
                    'name': 'Git Repository Exposure',
                    'url': '/.git/config',
                    'check': lambda r: '[core]' in r.text.lower()
                },
                {
                    'name': 'Environment File Exposure',
                    'url': '/.env',
                    'check': lambda r: 'database' in r.text.lower() or 'password' in r.text.lower()
                }
            ]

            for test in test_cases:
                try:
                    response = requests.get(urljoin(self.target_url, test['url']), timeout=5)
                    if response.status_code == 200 and test['check'](response):
                        vulnerabilities.append({
                            'type': test['name'],
                            'url': test['url'],
                            'severity': 'HIGH',
                            'description': f'Exposed {test["name"].lower()}'
                        })
                except:
                    continue

            self.results['web_vulnerabilities'] = {
                'vulnerabilities': vulnerabilities,
                'total_found': len(vulnerabilities),
                'status': 'completed'
            }

            print(f"✅ Found {len(vulnerabilities)} web vulnerabilities")

        except Exception as e:
            self.results['web_vulnerabilities'] = {
                'error': str(e),
                'status': 'failed'
            }
            print(f"❌ Web vulnerability scan failed: {str(e)}")

    def run_header_security_check(self):
        """Check security headers"""
        print("🛡️  Checking Security Headers...")

        try:
            response = requests.get(self.target_url, timeout=10)

            security_headers = {
                'Strict-Transport-Security': response.headers.get('Strict-Transport-Security'),
                'X-Content-Type-Options': response.headers.get('X-Content-Type-Options'),
                'X-Frame-Options': response.headers.get('X-Frame-Options'),
                'X-XSS-Protection': response.headers.get('X-XSS-Protection'),
                'Content-Security-Policy': response.headers.get('Content-Security-Policy'),
                'Referrer-Policy': response.headers.get('Referrer-Policy'),
                'Permissions-Policy': response.headers.get('Permissions-Policy'),
            }

            missing_headers = []
            weak_headers = []

            # Check for missing critical headers
            critical_headers = ['X-Content-Type-Options', 'X-Frame-Options']
            for header in critical_headers:
                if not security_headers.get(header):
                    missing_headers.append(header)

            # Check HSTS for HTTPS
            if self.target_url.startswith('https://'):
                if not security_headers.get('Strict-Transport-Security'):
                    missing_headers.append('Strict-Transport-Security')

            self.results['security_headers'] = {
                'headers': security_headers,
                'missing_critical': missing_headers,
                'weak_configurations': weak_headers,
                'status': 'completed'
            }

            print(f"✅ Security headers checked. Missing: {len(missing_headers)}")

        except Exception as e:
            self.results['security_headers'] = {
                'error': str(e),
                'status': 'failed'
            }
            print(f"❌ Security headers check failed: {str(e)}")

    def run_directory_enumeration(self):
        """Run basic directory enumeration"""
        print("📁 Running Directory Enumeration...")

        try:
            common_dirs = [
                'admin', 'administrator', 'login', 'adminpanel', 'cpanel',
                'phpmyadmin', 'mysql', 'backup', 'backups', 'tmp', 'temp',
                'uploads', 'files', 'images', 'css', 'js', 'assets'
            ]

            found_dirs = []

            for directory in common_dirs:
                try:
                    url = urljoin(self.target_url, directory + '/')
                    response = requests.get(url, timeout=3)
                    if response.status_code == 200:
                        found_dirs.append(directory)
                except:
                    continue

            self.results['directory_enumeration'] = {
                'found_directories': found_dirs,
                'total_checked': len(common_dirs),
                'status': 'completed'
            }

            print(f"✅ Found {len(found_dirs)} accessible directories")

        except Exception as e:
            self.results['directory_enumeration'] = {
                'error': str(e),
                'status': 'failed'
            }
            print(f"❌ Directory enumeration failed: {str(e)}")

    def run_sql_injection_scan(self):
        """Run basic SQL injection scan"""
        print("💉 Running SQL Injection Scan...")

        try:
            sql_payloads = [
                "' OR '1'='1",
                "'; DROP TABLE users; --",
                "' UNION SELECT * FROM users --",
                "admin' --",
            ]

            vulnerable_endpoints = []

            # Test common endpoints
            test_endpoints = ['/search', '/login', '/products']

            for endpoint in test_endpoints:
                for payload in sql_payloads:
                    try:
                        params = {'q': payload, 'search': payload, 'query': payload}
                        response = requests.get(
                            urljoin(self.target_url, endpoint),
                            params=params,
                            timeout=3
                        )

                        # Check for SQL error patterns
                        sql_errors = [
                            'sql syntax', 'mysql error', 'postgresql error',
                            'sqlite error', 'oracle error', 'sql server error'
                        ]

                        response_text = response.text.lower()
                        if any(error in response_text for error in sql_errors):
                            vulnerable_endpoints.append({
                                'endpoint': endpoint,
                                'payload': payload,
                                'error_pattern': 'SQL syntax error detected'
                            })
                            break
                    except:
                        continue

            self.results['sql_injection'] = {
                'vulnerable_endpoints': vulnerable_endpoints,
                'total_tested': len(test_endpoints) * len(sql_payloads),
                'status': 'completed'
            }

            print(f"✅ SQL injection scan completed. Vulnerabilities: {len(vulnerable_endpoints)}")

        except Exception as e:
            self.results['sql_injection'] = {
                'error': str(e),
                'status': 'failed'
            }
            print(f"❌ SQL injection scan failed: {str(e)}")

    def run_xss_scan(self):
        """Run basic XSS scan"""
        print("⚠️  Running XSS Scan...")

        try:
            xss_payloads = [
                '<script>alert("XSS")</script>',
                '<img src=x onerror=alert("XSS")>',
                'javascript:alert("XSS")',
            ]

            vulnerable_endpoints = []

            # Test common input fields
            test_endpoints = ['/search', '/contact', '/feedback']

            for endpoint in test_endpoints:
                for payload in xss_payloads:
                    try:
                        data = {
                            'q': payload,
                            'search': payload,
                            'message': payload,
                            'comment': payload,
                            'name': payload
                        }

                        response = requests.post(
                            urljoin(self.target_url, endpoint),
                            data=data,
                            timeout=3
                        )

                        if payload in response.text:
                            vulnerable_endpoints.append({
                                'endpoint': endpoint,
                                'payload': payload,
                                'type': 'Reflected XSS'
                            })
                            break
                    except:
                        continue

            self.results['xss_scan'] = {
                'vulnerable_endpoints': vulnerable_endpoints,
                'total_tested': len(test_endpoints) * len(xss_payloads),
                'status': 'completed'
            }

            print(f"✅ XSS scan completed. Vulnerabilities: {len(vulnerable_endpoints)}")

        except Exception as e:
            self.results['xss_scan'] = {
                'error': str(e),
                'status': 'failed'
            }
            print(f"❌ XSS scan failed: {str(e)}")

    def generate_report(self):
        """Generate comprehensive security report"""
        print("\n" + "=" * 60)
        print("🔒 SECURITY SCAN REPORT")
        print("=" * 60)

        report = {
            'scan_info': {
                'target_url': self.target_url,
                'target_host': self.target_host,
                'scan_start': self.scan_start_time.isoformat(),
                'scan_end': self.scan_end_time.isoformat(),
                'duration_seconds': (self.scan_end_time - self.scan_start_time).total_seconds()
            },
            'results': self.results,
            'summary': self._generate_summary()
        }

        # Save report to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f"security_scan_report_{timestamp}.json"

        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        print(f"📄 Report saved to: {report_file}")

        # Print summary
        self._print_summary()

    def _generate_summary(self):
        """Generate scan summary"""
        summary = {
            'total_vulnerabilities': 0,
            'high_severity': 0,
            'medium_severity': 0,
            'low_severity': 0,
            'scan_success_rate': 0
        }

        total_scans = len(self.results)
        successful_scans = 0

        for scan_name, scan_result in self.results.items():
            if scan_result.get('status') == 'completed':
                successful_scans += 1

                # Count vulnerabilities
                if scan_name == 'web_vulnerabilities':
                    vulns = scan_result.get('vulnerabilities', [])
                    summary['total_vulnerabilities'] += len(vulns)
                    summary['high_severity'] += len([v for v in vulns if v.get('severity') == 'HIGH'])

                elif scan_name == 'sql_injection':
                    summary['total_vulnerabilities'] += len(scan_result.get('vulnerable_endpoints', []))
                    summary['high_severity'] += len(scan_result.get('vulnerable_endpoints', []))

                elif scan_name == 'xss_scan':
                    summary['total_vulnerabilities'] += len(scan_result.get('vulnerable_endpoints', []))
                    summary['medium_severity'] += len(scan_result.get('vulnerable_endpoints', []))

        summary['scan_success_rate'] = (successful_scans / total_scans * 100) if total_scans > 0 else 0

        return summary

    def _print_summary(self):
        """Print scan summary to console"""
        summary = self._generate_summary()

        print("\n📊 SCAN SUMMARY")
        print(f"Total Vulnerabilities: {summary['total_vulnerabilities']}")
        print(f"High Severity: {summary['high_severity']}")
        print(f"Medium Severity: {summary['medium_severity']}")
        print(f"Low Severity: {summary['low_severity']}")
        print(f"Scan Success Rate: {summary['scan_success_rate']:.1f}%")
        # Security rating
        if summary['total_vulnerabilities'] == 0:
            print("Security Rating: 🟢 EXCELLENT")
        elif summary['high_severity'] == 0:
            print("Security Rating: 🟡 GOOD")
        elif summary['high_severity'] <= 2:
            print("Security Rating: 🟠 FAIR")
        else:
            print("Security Rating: 🔴 POOR")

        print("\n🔍 Scan Details:")
        for scan_name, result in self.results.items():
            status = result.get('status', 'unknown')
            icon = "✅" if status == 'completed' else "❌"
            print(f"{icon} {scan_name.replace('_', ' ').title()}: {status}")


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description='Security Scanner for Retail Management System')
    parser.add_argument('url', help='Target URL to scan')
    parser.add_argument('--host', help='Target host/IP (optional)')
    parser.add_argument('--port', type=int, default=80, help='Target port (default: 80)')

    args = parser.parse_args()

    scanner = SecurityScanner(args.url, args.host, args.port)
    scanner.start_scan()


if __name__ == '__main__':
    main()
