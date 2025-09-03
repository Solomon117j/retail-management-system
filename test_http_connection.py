#!/usr/bin/env python3
"""
Test HTTP connection to the Django development server
"""

import urllib.request
import urllib.error
import socket
import sys

def test_http_connection():
    """Test the HTTP connection to localhost:8000"""

    print("Testing HTTP connection to http://127.0.0.1:8000")
    print("=" * 50)

    # Test 1: Basic HTTP connection
    print("\n1. Testing basic HTTP connection...")
    try:
        req = urllib.request.Request('http://127.0.0.1:8000/')
        with urllib.request.urlopen(req, timeout=10) as response:
            print("✅ HTTP connection successful")
            print(f"   Status: {response.getcode()}")
            print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")

            # Read first 500 characters of response
            content = response.read(500).decode('utf-8', errors='ignore')
            print(f"   Response preview: {content[:200]}...")

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

    print("\n" + "=" * 50)
    print("HTTP connection test completed")
    return True

if __name__ == "__main__":
    success = test_http_connection()
    sys.exit(0 if success else 1)
