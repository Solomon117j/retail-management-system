#!/usr/bin/env python3
"""
Test SSL connection to the Django development server
"""

import ssl
import socket
import urllib.request
import urllib.error
from datetime import datetime
import sys

def test_ssl_connection():
    """Test the SSL connection to localhost:8000"""

    print("Testing SSL connection to https://127.0.0.1:8000")
    print("=" * 60)

    # Test 1: Basic HTTPS connection
    print("\n1. Testing basic HTTPS connection...")
    try:
        # Create SSL context that accepts self-signed certificates
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        # Test connection
        with socket.create_connection(('127.0.0.1', 8000)) as sock:
            with context.wrap_socket(sock, server_hostname='localhost') as ssock:
                print("✅ SSL connection established successfully")
                print(f"   Protocol: {ssock.version}")
                print(f"   Cipher: {ssock.cipher()}")

                # Get certificate info
                cert = ssock.getpeercert()
                if cert:
                    print("✅ Certificate received")
                    subject = dict(x[0] for x in cert['subject'])
                    issuer = dict(x[0] for x in cert['issuer'])

                    print(f"   Subject: {subject.get('commonName', 'N/A')}")
                    print(f"   Issuer: {issuer.get('commonName', 'N/A')}")

                    # Check validity dates
                    not_before = datetime.strptime(cert['notBefore'], '%b %d %H:%M:%S %Y %Z')
                    not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    now = datetime.now()

                    print(f"   Valid from: {not_before}")
                    print(f"   Valid until: {not_after}")

                    if now < not_before:
                        print("❌ Certificate is not yet valid")
                    elif now > not_after:
                        print("❌ Certificate has expired")
                    else:
                        print("✅ Certificate is currently valid")
                else:
                    print("❌ No certificate received")

    except Exception as e:
        print(f"❌ SSL connection failed: {e}")
        return False

    # Test 2: HTTP request
    print("\n2. Testing HTTP request...")
    try:
        # Create custom opener that accepts self-signed certificates
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=context))
        urllib.request.install_opener(opener)

        req = urllib.request.Request('https://127.0.0.1:8000/')
        with urllib.request.urlopen(req) as response:
            print("✅ HTTP request successful")
            print(f"   Status: {response.getcode()}")
            print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")

            # Read first 500 characters of response
            content = response.read(500).decode('utf-8', errors='ignore')
            print(f"   Response preview: {content[:200]}...")

    except urllib.error.URLError as e:
        print(f"❌ HTTP request failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

    # Test 3: Check certificate file directly
    print("\n3. Checking certificate file...")
    try:
        with open('certs/devserver.crt', 'r') as f:
            cert_content = f.read()
            if 'BEGIN CERTIFICATE' in cert_content and 'END CERTIFICATE' in cert_content:
                print("✅ Certificate file is properly formatted")
                print(f"   File size: {len(cert_content)} characters")
            else:
                print("❌ Certificate file appears malformed")
    except FileNotFoundError:
        print("❌ Certificate file not found")
    except Exception as e:
        print(f"❌ Error reading certificate file: {e}")

    print("\n" + "=" * 60)
    print("SSL connection test completed")
    return True

if __name__ == "__main__":
    success = test_ssl_connection()
    sys.exit(0 if success else 1)
