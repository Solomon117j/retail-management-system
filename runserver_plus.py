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

    # Check if SSL certificates exist
    cert_file = Path("certs/devserver.crt")
    key_file = Path("certs/devserver.key")

    if not cert_file.exists() or not key_file.exists():
        print("SSL certificates not found. Generating new certificates...")
        try:
            # Run the certificate generation script
            result = subprocess.run([sys.executable, 'generate_ssl_certs.py'], check=True)
            print("SSL certificates generated successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error generating certificates: {e}")
            print("Please run 'python generate_ssl_certs.py' manually to generate certificates.")
            sys.exit(1)

    # Run the runserver_plus command with SSL support
    try:
        print("Starting Django development server with SSL support...")
        print("Access the site at: https://127.0.0.1:8000")
        print("Note: You may see a security warning in your browser due to self-signed certificate.")
        print("Press Ctrl+C to stop the server")
        print("-" * 70)

        # Run the command with SSL support
        cmd = [
            sys.executable, 'manage.py', 'runserver_plus',
            '127.0.0.1:8000',
            '--cert', str(cert_file),
            '--key', str(key_file)
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
