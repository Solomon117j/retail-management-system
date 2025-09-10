#!/usr/bin/env python
"""
Simple test to check PostgreSQL connection for staging environment.
"""

import os
import subprocess
from pathlib import Path

def test_connection():
    print("Testing PostgreSQL connection...")

    # Check if .env.staging exists
    env_file = Path('.env.staging')
    if env_file.exists():
        print("✓ .env.staging file found")
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
            print("✓ Environment variables loaded")
        except ImportError:
            print("⚠ python-dotenv not available")
    else:
        print("✗ .env.staging file not found")

    # Get database config
    db_user = os.environ.get('POSTGRES_USER_STAGING', 'admin_user')
    db_password = os.environ.get('POSTGRES_PASSWORD_STAGING', 'Only4u@12345')
    db_name = os.environ.get('POSTGRES_DB_STAGING', 'retail_management_staging')

    print(f"User: {db_user}")
    print(f"Password: {'*' * len(db_password)}")
    print(f"Database: {db_name}")

    # Test connection
    try:
        result = subprocess.run([
            'psql',
            '-h', '127.0.0.1',
            '-p', '5432',
            '-U', db_user,
            '-d', db_name,
            '-c', 'SELECT current_user, current_database();'
        ], capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            print("✓ Connection successful!")
            print("Output:", result.stdout.strip())
        else:
            print("✗ Connection failed!")
            print("Error:", result.stderr.strip())
    except Exception as e:
        print(f"✗ Exception: {e}")

if __name__ == '__main__':
    test_connection()
