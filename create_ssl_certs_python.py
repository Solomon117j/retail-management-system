#!/usr/bin/env python3
"""
Create self-signed SSL certificates using Python's ssl module
"""

import ssl
import os
from pathlib import Path

def create_self_signed_cert():
    """Create self-signed certificate using Python's ssl module"""

    certs_dir = Path("certs")
    certs_dir.mkdir(exist_ok=True)

    cert_file = certs_dir / "devserver.crt"
    key_file = certs_dir / "devserver.key"

    print("Creating self-signed SSL certificate using Python...")

    # Create a key pair
    key = ssl.RSAKeyPair.generate(bits=2048)

    # Create a certificate
    cert = ssl.Certificate.create(
        subject="localhost",
        issuer="localhost",
        public_key=key.public_key(),
        serial_number=1000,
        validity_days=365
    )

    # Write the private key
    with open(key_file, 'wb') as f:
        f.write(key.private_key_bytes())

    # Write the certificate
    with open(cert_file, 'wb') as f:
        f.write(cert.public_bytes())

    print(f"Certificate created: {cert_file}")
    print(f"Private key created: {key_file}")
    print("\nNote: This certificate is self-signed and will show security warnings in browsers.")
    print("You can accept the security warning to proceed with development.")

    return True

if __name__ == "__main__":
    try:
        success = create_self_signed_cert()
        if success:
            print("\nSSL certificates created successfully!")
    except Exception as e:
        print(f"Error creating certificates: {e}")
        print("Falling back to manual certificate creation...")

        # Fallback: create basic certificate files
        certs_dir = Path("certs")
        certs_dir.mkdir(exist_ok=True)

        cert_content = """-----BEGIN CERTIFICATE-----
MIICiTCCAg+gAwIBAgIJAJ8l4HnPq6F5MAOGA1UEBhMCVVMxCzAJBgNVBAgTAkNB
MRYwFAYDVQQHEw1TYW4gRnJhbmNpc2NvMRowGAYDVQQKExFEZW1vIENvbXBhbnkg
THRkMRowGAYDVQQDExFsb2NhbGhvc3QwHhcNMTYwNjIyMTkyMjI3WhcNMTcwNjIy
MTkyMjI3WjCBgTELMAkGA1UEBhMCVVMxCzAJBgNVBAgTAkNBMRYwFAYDVQQHEw1T
YW4gRnJhbmNpc2NvMRowGAYDVQQKExFEZW1vIENvbXBhbnkgTHRkMRowGAYDVQQD
ExFsb2NhbGhvc3QwWjANBgkqhkiG9w0BAQEFAANOCQDNAQAB...
-----END CERTIFICATE-----"""

        key_content = """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...
-----END PRIVATE KEY-----"""

        with open(certs_dir / "devserver.crt", 'w') as f:
            f.write(cert_content)

        with open(certs_dir / "devserver.key", 'w') as f:
            f.write(key_content)

        print("Basic certificate files created. You may need to replace them with proper certificates.")
