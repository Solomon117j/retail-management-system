#!/usr/bin/env python3
"""
Test multiple endpoints to verify middleware fixes
"""

import urllib.request
import urllib.error
import socket
import sys

def test_endpoint(url, description):
    """Test a specific endpoint"""
    print(f"\nTesting {description}: {url}")
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as response:
            print(f"✅ Success: {response.getcode()}")
            return True
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP error: {e.code} - {e.reason}")
        return False
    except urllib.error.URLError as e:
        print(f"❌ URL error: {e.reason}")
        return False
    except socket.timeout:
        print("❌ Connection timeout")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    base_url = 'http://127.0.0.1:8000'

    endpoints = [
        ('/', 'Root page'),
        ('/accounts/login/', 'Login choice page'),
        ('/accounts/login/generic/', 'Generic login page'),
        ('/accounts/login/customer/', 'Customer login page'),
        ('/accounts/login/staff/', 'Staff login page'),
        ('/accounts/register/', 'Registration page'),
        ('/accounts/logout/', 'Logout page'),
        ('/admin/login/', 'Admin login page'),
        ('/static/css/style.css', 'Static CSS file'),
        ('/media/', 'Media files'),
    ]

    print("Testing multiple endpoints...")
    print("=" * 50)

    all_success = True
    for path, desc in endpoints:
        url = base_url + path
        success = test_endpoint(url, desc)
        if not success:
            all_success = False

    print("\n" + "=" * 50)
    if all_success:
        print("All endpoints tested successfully!")
    else:
        print("Some endpoints failed.")

    return all_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
