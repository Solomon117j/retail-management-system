#!/usr/bin/env python3
"""
Generate proper self-signed SSL certificates using cryptography library
"""

from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from datetime import datetime, timedelta
import os
from pathlib import Path

def generate_proper_ssl_certificates():
    """Generate proper self-signed SSL certificates"""

    # Create certs directory
    certs_dir = Path("certs")
    certs_dir.mkdir(exist_ok=True)

    cert_file = certs_dir / "devserver.crt"
    key_file = certs_dir / "devserver.key"

    print("Generating proper self-signed SSL certificates...")

    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    # Create certificate
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "State"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "City"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Development"),
        x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
    ])

    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.utcnow()
    ).not_valid_after(
        datetime.utcnow() + timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName("localhost"),
            x509.DNSName("127.0.0.1"),
        ]),
        critical=False,
    ).sign(private_key, hashes.SHA256(), default_backend())

    # Write private key
    with open(key_file, 'wb') as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))

    # Write certificate
    with open(cert_file, 'wb') as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    print(f"Certificate generated: {cert_file}")
    print(f"Private key generated: {key_file}")
    print("Certificates are in proper PEM format for Django runserver_plus")

    return True

if __name__ == "__main__":
    try:
        success = generate_proper_ssl_certificates()
        if success:
            print("\nSSL certificates generated successfully!")
            print("You can now run: python runserver_plus.py")
    except Exception as e:
        print(f"Error generating certificates: {e}")
        print("Make sure cryptography library is installed: pip install cryptography")
