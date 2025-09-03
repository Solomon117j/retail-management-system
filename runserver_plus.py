#!/usr/bin/env python
"""
Script to run Django development server with runserver_plus from django-extensions.
This provides enhanced features like SSL support, Werkzeug debugger, etc.
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    # Add the current directory to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)

    # Set Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retail_management_system.settings')

    # SSL certificate paths
    certs_dir = Path(current_dir) / "certs"
    cert_file = certs_dir / "devserver.crt"
    key_file = certs_dir / "devserver.key"

    # Check if certificates exist
    if not cert_file.exists() or not key_file.exists():
        print("SSL certificates not found. Generating certificates...")
        try:
            subprocess.run([sys.executable, 'generate_proper_ssl_certs.py'], check=True)
        except subprocess.CalledProcessError:
            print("Failed to generate certificates. Please run generate_proper_ssl_certs.py manually.")
            sys.exit(1)

    # Run the runserver_plus command with SSL
    try:
        print("Starting Django development server with runserver_plus (HTTPS)...")
        print("Enhanced features available: SSL support, Werkzeug debugger, etc.")
        print(f"SSL Certificate: {cert_file}")
        print(f"SSL Private Key: {key_file}")
        print("Access the site at: https://127.0.0.1:8000")
        print("Note: You may need to accept the security warning for the self-signed certificate")
        print("Press Ctrl+C to stop the server")
        print("-" * 70)

        # Run the command with SSL support
        cmd = [
            sys.executable, 'manage.py', 'runserver_plus',
            '--cert', str(cert_file),
            '--key', str(key_file),
            '127.0.0.1:8000'
        ]
        subprocess.run(cmd, check=True)

    except subprocess.CalledProcessError as e:
        print(f"Error running server: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nServer stopped by user.")
        sys.exit(0)

if __name__ == '__main__':
    main()
