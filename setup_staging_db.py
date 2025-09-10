#!/usr/bin/env python
"""
Script to set up PostgreSQL database for staging environment.
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a shell command and return success status."""
    print(f"Running: {description}")
    print(f"Command: {command}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def main():
    # Load staging environment variables
    project_dir = Path(__file__).resolve().parent
    env_file = project_dir / '.env.staging'

    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv(env_file)
        print("Loaded staging environment variables")
    else:
        print("Warning: .env.staging not found. Using environment variables.")

    # Get database configuration
    db_name = os.environ.get('POSTGRES_DB_STAGING', 'retail_management_staging')
    db_user = os.environ.get('POSTGRES_USER_STAGING', 'admin_user')
    db_password = os.environ.get('POSTGRES_PASSWORD_STAGING', 'Only4u@12345')
    db_host = os.environ.get('POSTGRES_HOST_STAGING', '127.0.0.1')
    db_port = os.environ.get('POSTGRES_PORT_STAGING', '5432')

    print("\nStaging Database Setup")
    print(f"Database: {db_name}")
    print(f"User: {db_user}")
    print(f"Host: {db_host}:{db_port}")
    print("-" * 50)

    # Check if PostgreSQL is running
    if not run_command("pg_isready -h localhost -p 5432", "Check PostgreSQL connection"):
        print("PostgreSQL is not running or not accessible.")
        print("Please start PostgreSQL service and try again.")
        sys.exit(1)

    # Create database user if it doesn't exist
    create_user_cmd = f'psql -h {db_host} -p {db_port} -U postgres -c "CREATE USER IF NOT EXISTS {db_user} WITH PASSWORD \'{db_password}\';"'
    if not run_command(create_user_cmd, "Create database user"):
        print("Failed to create database user. You may need to run this with postgres superuser privileges.")
        sys.exit(1)

    # Create database if it doesn't exist
    create_db_cmd = f'psql -h {db_host} -p {db_port} -U postgres -c "CREATE DATABASE {db_name} OWNER {db_user};"'
    if not run_command(create_db_cmd, "Create staging database"):
        print("Failed to create database. It may already exist or you may need different permissions.")
        sys.exit(1)

    # Grant privileges
    grant_cmd = f'psql -h {db_host} -p {db_port} -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_user};"'
    if not run_command(grant_cmd, "Grant database privileges"):
        print("Failed to grant privileges.")
        sys.exit(1)

    print("\n✓ Staging database setup completed successfully!")
    print(f"Database: {db_name}")
    print(f"User: {db_user}")
    print("\nNext steps:")
    print("1. Run migrations: python manage.py migrate --settings=retail_management_system.settings_staging")
    print("2. Create superuser: python manage.py createsuperuser --settings=retail_management_system.settings_staging")
    print("3. Start staging server: python run_staging.py")

if __name__ == '__main__':
    main()
