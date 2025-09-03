#!/usr/bin/env python3
"""
Penetration Testing Suite for Retail Management System
Automated security testing framework
"""

import os
import sys
import django
import requests
import time
import json
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retail_management_system.settings')
django.setup()

from django.test import TestCase, Client, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from accounts.models import User

class PenetrationTestSuite(TestCase):
    """
    Comprehensive penetration testing suite for the Retail Management System
    """

    def setUp(self):
        """Set up test environment"""
        self.client = Client()
        self.base_url = 'http://localhost:8000'

        # Create test users
        self.test_user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPassword123!',
            first_name='Test',
            last_name='User'
        )

        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='AdminPassword123!',
            first_name='Admin',
            last_name='User'
        )

        # Test data
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'warnings': 0,
            'tests': []
        }

    def tearDown(self):
        """Clean up test data"""
        self.test_user.delete()
        self.admin_user.delete()

    def log_test_result(self, test_name, result, details=None):
        """Log test result"""
        self.test_results['tests'].append({
            'name': test_name,
            'result': result,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })

        if result == 'PASS':
            self.test_results['passed'] += 1
        elif result == 'FAIL':
            self.test_results['failed'] += 1
        elif result == 'WARN':
            self.test_results['warnings'] += 1

    # === AUTHENTICATION TESTING ===

    def test_brute_force_protection(self):
        """Test brute force attack protection"""
        print("Testing brute force protection...")

        # Attempt multiple failed logins
        failed_attempts = 0
        max_attempts = 10

        for i in range(max_attempts):
            response = self.client.post('/accounts/login/', {
                'username': 'testuser',
                'password': 'wrongpassword123',
                'csrfmiddlewaretoken': self.client.cookies.get('csrftoken', '').value
            })

            if response.status_code == 401 or 'Invalid credentials' in response.content.decode():
                failed_attempts += 1
            time.sleep(0.1)  # Small delay to avoid being too aggressive

        # Check if account is locked after multiple attempts
        response = self.client.post('/accounts/login/', {
            'username': 'testuser',
            'password': 'TestPassword123!',
            'csrfmiddlewaretoken': self.client.cookies.get('csrftoken', '').value
        })

        if response.status_code == 423:  # Locked
            self.log_test_result('Brute Force Protection', 'PASS', 'Account locked after multiple failed attempts')
        elif failed_attempts < max_attempts:
            self.log_test_result('Brute Force Protection', 'WARN', 'Some login attempts succeeded unexpectedly')
        else:
            self.log_test_result('Brute Force Protection', 'FAIL', 'No brute force protection detected')

    def test_password_policy(self):
        """Test password policy enforcement"""
        print("Testing password policy...")

        weak_passwords = [
            'short',
            '12345678',
            'password',
            'qwerty123',
            'admin123'
        ]

        for password in weak_passwords:
            try:
                from django.contrib.auth.password_validation import validate_password
                validate_password(password)
                self.log_test_result('Password Policy', 'FAIL', f'Weak password "{password}" was accepted')
                return
            except:
                continue

        # Test strong password
        try:
            from django.contrib.auth.password_validation import validate_password
            validate_password('MySecurePassword123!')
            self.log_test_result('Password Policy', 'PASS', 'Strong password policy enforced')
        except Exception as e:
            self.log_test_result('Password Policy', 'FAIL', f'Strong password rejected: {str(e)}')

    def test_session_security(self):
        """Test session security"""
        print("Testing session security...")

        # Login and get session
        self.client.login(username='testuser', password='TestPassword123!')
        session_id = self.client.session.session_key

        # Test session persistence
        response = self.client.get('/')
        if response.status_code == 200:
            self.log_test_result('Session Security', 'PASS', 'Session maintained correctly')
        else:
            self.log_test_result('Session Security', 'FAIL', 'Session not maintained')

        # Test session invalidation on logout
        self.client.logout()
        response = self.client.get('/')
        if response.status_code == 302:  # Redirect to login
            self.log_test_result('Session Security', 'PASS', 'Session invalidated on logout')
        else:
            self.log_test_result('Session Security', 'WARN', 'Session may not be properly invalidated')

    # === AUTHORIZATION TESTING ===

    def test_privilege_escalation(self):
        """Test for privilege escalation vulnerabilities"""
        print("Testing privilege escalation...")

        # Login as regular user
        self.client.login(username='testuser', password='TestPassword123!')

        # Attempt to access admin-only resources
        admin_urls = [
            '/admin/',
            '/accounts/user/add/',
            '/human_resources/employee/add/',
        ]

        for url in admin_urls:
            response = self.client.get(url)
            if response.status_code == 403:
                self.log_test_result('Privilege Escalation', 'PASS', f'Access denied to {url}')
            elif response.status_code == 200:
                self.log_test_result('Privilege Escalation', 'FAIL', f'Unauthorized access to {url}')
            else:
                self.log_test_result('Privilege Escalation', 'WARN', f'Unexpected response for {url}: {response.status_code}')

    def test_direct_object_reference(self):
        """Test for direct object reference vulnerabilities"""
        print("Testing direct object references...")

        # Login as regular user
        self.client.login(username='testuser', password='TestPassword123!')

        # Attempt to access other users' data
        other_user_id = self.admin_user.id
        test_urls = [
            f'/accounts/user/{other_user_id}/change/',
            f'/human_resources/employee/{other_user_id}/',
        ]

        for url in test_urls:
            response = self.client.get(url)
            if response.status_code == 403:
                self.log_test_result('Direct Object Reference', 'PASS', f'Access denied to {url}')
            elif response.status_code == 200:
                self.log_test_result('Direct Object Reference', 'FAIL', f'Unauthorized access to {url}')
            else:
                self.log_test_result('Direct Object Reference', 'WARN', f'Unexpected response for {url}: {response.status_code}')

    # === INPUT VALIDATION TESTING ===

    def test_sql_injection(self):
        """Test for SQL injection vulnerabilities"""
        print("Testing SQL injection protection...")

        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM users --",
            "admin' --",
            "' OR 1=1 --",
        ]

        vulnerable = False

        for payload in sql_payloads:
            # Test login form
            response = self.client.post('/accounts/login/', {
                'username': payload,
                'password': 'password',
                'csrfmiddlewaretoken': self.client.cookies.get('csrftoken', '').value
            })

            if 'sql' in response.content.decode().lower() or response.status_code == 500:
                vulnerable = True
                break

            # Test search forms if available
            response = self.client.get('/inventory/', {'search': payload})
            if 'sql' in response.content.decode().lower() or response.status_code == 500:
                vulnerable = True
                break

        if not vulnerable:
            self.log_test_result('SQL Injection', 'PASS', 'No SQL injection vulnerabilities detected')
        else:
            self.log_test_result('SQL Injection', 'FAIL', 'SQL injection vulnerability detected')

    def test_xss_protection(self):
        """Test for XSS vulnerabilities"""
        print("Testing XSS protection...")

        xss_payloads = [
            '<script>alert("XSS")</script>',
            '<img src=x onerror=alert("XSS")>',
            'javascript:alert("XSS")',
            '<iframe src="javascript:alert(\'XSS\')"></iframe>',
        ]

        vulnerable = False

        for payload in xss_payloads:
            # Test in forms that accept user input
            response = self.client.post('/inventory/product/add/', {
                'name': payload,
                'description': 'Test product',
                'csrfmiddlewaretoken': self.client.cookies.get('csrftoken', '').value
            })

            if payload in response.content.decode():
                vulnerable = True
                break

        if not vulnerable:
            self.log_test_result('XSS Protection', 'PASS', 'XSS protection working correctly')
        else:
            self.log_test_result('XSS Protection', 'FAIL', 'XSS vulnerability detected')

    def test_csrf_protection(self):
        """Test CSRF protection"""
        print("Testing CSRF protection...")

        # Attempt POST request without CSRF token
        response = self.client.post('/inventory/product/add/', {
            'name': 'Test Product',
            'description': 'Test Description'
        })

        if response.status_code == 403:
            self.log_test_result('CSRF Protection', 'PASS', 'CSRF protection working')
        else:
            self.log_test_result('CSRF Protection', 'FAIL', 'CSRF protection not enforced')

    # === FILE UPLOAD TESTING ===

    def test_file_upload_security(self):
        """Test file upload security"""
        print("Testing file upload security...")

        # Test malicious file upload
        malicious_files = [
            ('malicious.php', '<?php echo "Malicious"; ?>', 'application/x-php'),
            ('script.js', 'alert("XSS");', 'application/javascript'),
            ('exploit.exe', 'MZ\x90\x00\x03\x00\x00\x00', 'application/octet-stream'),
        ]

        for filename, content, mimetype in malicious_files:
            file_obj = SimpleUploadedFile(filename, content.encode(), content_type=mimetype)

            response = self.client.post('/upload/', {
                'file': file_obj,
                'csrfmiddlewaretoken': self.client.cookies.get('csrftoken', '').value
            })

            if response.status_code == 400 or 'not allowed' in response.content.decode().lower():
                self.log_test_result('File Upload Security', 'PASS', f'Malicious file {filename} rejected')
            else:
                self.log_test_result('File Upload Security', 'FAIL', f'Malicious file {filename} accepted')

    # === API TESTING ===

    def test_api_security(self):
        """Test API security"""
        print("Testing API security...")

        # Test unauthenticated API access
        api_endpoints = [
            '/api/products/',
            '/api/users/',
            '/api/sales/',
        ]

        for endpoint in api_endpoints:
            response = self.client.get(endpoint)
            if response.status_code == 401:
                self.log_test_result('API Security', 'PASS', f'API {endpoint} requires authentication')
            elif response.status_code == 200:
                self.log_test_result('API Security', 'WARN', f'API {endpoint} allows unauthenticated access')
            else:
                self.log_test_result('API Security', 'INFO', f'API {endpoint} returned {response.status_code}')

    # === UTILITY METHODS ===

    def run_all_tests(self):
        """Run all penetration tests"""
        print("Starting Penetration Testing Suite...")
        print("=" * 50)

        test_methods = [
            self.test_brute_force_protection,
            self.test_password_policy,
            self.test_session_security,
            self.test_privilege_escalation,
            self.test_direct_object_reference,
            self.test_sql_injection,
            self.test_xss_protection,
            self.test_csrf_protection,
            self.test_file_upload_security,
            self.test_api_security,
        ]

        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                self.log_test_result(test_method.__name__, 'ERROR', str(e))

        self.generate_report()

    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 50)
        print("PENETRATION TESTING REPORT")
        print("=" * 50)

        print(f"Tests Passed: {self.test_results['passed']}")
        print(f"Tests Failed: {self.test_results['failed']}")
        print(f"Warnings: {self.test_results['warnings']}")
        print(f"Total Tests: {len(self.test_results['tests'])}")

        print("\nDetailed Results:")
        print("-" * 30)

        for test in self.test_results['tests']:
            status_icon = {
                'PASS': '✅',
                'FAIL': '❌',
                'WARN': '⚠️',
                'ERROR': '🔥'
            }.get(test['result'], '?')

            print(f"{status_icon} {test['name']}: {test['result']}")
            if test['details']:
                print(f"   {test['details']}")

        # Save report to file
        report_file = f"penetration_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)

        print(f"\nReport saved to: {report_file}")

        # Security score
        total_tests = len(self.test_results['tests'])
        if total_tests > 0:
            score = (self.test_results['passed'] / total_tests) * 100
            print(f"Security Score: {score:.1f}")
            if score >= 90:
                print("Security Rating: 🟢 EXCELLENT")
            elif score >= 75:
                print("Security Rating: 🟡 GOOD")
            elif score >= 60:
                print("Security Rating: 🟠 FAIR")
            else:
                print("Security Rating: 🔴 POOR")


if __name__ == '__main__':
    suite = PenetrationTestSuite()
    suite.setUp()
    suite.run_all_tests()
    suite.tearDown()
