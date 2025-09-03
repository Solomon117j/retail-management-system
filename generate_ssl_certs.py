#!/usr/bin/env python3
"""
Script to generate self-signed SSL certificates for Django development server
"""

import os
import subprocess
from pathlib import Path

def generate_ssl_certificates():
    """Generate self-signed SSL certificates for development"""

    # Create certs directory
    certs_dir = Path("certs")
    certs_dir.mkdir(exist_ok=True)

    cert_file = certs_dir / "devserver.crt"
    key_file = certs_dir / "devserver.key"

    print("Generating self-signed SSL certificate for development...")

    # Use OpenSSL to generate certificate
    try:
        # Generate private key
        subprocess.run([
            "openssl", "genrsa", "-out", str(key_file), "2048"
        ], check=True)

        # Generate certificate
        subprocess.run([
            "openssl", "req", "-new", "-x509", "-key", str(key_file),
            "-out", str(cert_file), "-days", "365", "-subj",
            "/C=US/ST=State/L=City/O=Organization/CN=localhost"
        ], check=True)

        print(f"SSL certificates generated successfully:")
        print(f"  Certificate: {cert_file}")
        print(f"  Private Key: {key_file}")

        return True

    except subprocess.CalledProcessError as e:
        print(f"Error generating certificates: {e}")
        print("Make sure OpenSSL is installed and available in your PATH")
        return False
    except FileNotFoundError:
        print("OpenSSL not found. Please install OpenSSL and try again.")
        return False

if __name__ == "__main__":
    success = generate_ssl_certificates()
    if not success:
        print("\nAlternative: You can generate certificates manually using:")
        print("openssl genrsa -out certs/devserver.key 2048")
        print("openssl req -new -x509 -key certs/devserver.key -out certs/devserver.crt -days 365 -subj '/C=US/ST=State/L=City/O=Organization/CN=localhost'")
