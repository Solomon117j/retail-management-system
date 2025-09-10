#!/usr/bin/env python
"""
Script to diagnose PostgreSQL database connection issues for staging environment.
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a shell command and return the result."""
    print(f"\n{description}")
    print(f"Command: {command}")
    print("-" * 50)
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✓ SUCCESS")
            if result.stdout:
                print("Output:")
                print(result.stdout.strip())
        else:
            print("✗ FAILED")
            if result.stderr:
                print("Error:")
                print(result.stderr.strip())
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        print("✗ TIMEOUT - Command took too long")
        return False, "", "Command timeout"
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False, "", str(e)
    finally:
        pass

def main():
    print("PostgreSQL Database Connection Diagnostic Tool")
    print("=" * 60)

    # Load staging environment variables
    project_dir = Path(__file__).resolve().parent
    env_file = project_dir / '.env.staging'

    if env_file.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
            print("✓ Loaded staging environment variables from .env.staging")
        except ImportError:
            print("⚠ Warning: python-dotenv not installed, using system environment variables")
    else:
        print("⚠ Warning: .env.staging file not found")

    # Get database configuration from environment
    db_name = os.environ.get('POSTGRES_DB_STAGING', 'retail_management_staging')
    db_user = os.environ.get('POSTGRES_USER_STAGING', 'admin_user')
    db_password = os.environ.get('POSTGRES_PASSWORD_STAGING', 'Only4u@12345')
    db_host = os.environ.get('POSTGRES_HOST_STAGING', '127.0.0.1')
    db_port = os.environ.get('POSTGRES_PORT_STAGING', '5432')

    print("Database Configuration:")
    print(f"  Database: {db_name}")
    print(f"  User: {db_user}")
    print(f"  Password: {'*' * len(db_password) if db_password else 'NOT SET'}")
    print(f"  Host: {db_host}:{db_port}")

    # Test 1: Check if PostgreSQL is running
    success, output, error = run_command("pg_isready -h 127.0.0.1 -p 5432", "Test 1: Check PostgreSQL server status")

    if not success:
        print("\n❌ PostgreSQL server is not running or not accessible.")
        print("Solution: Start PostgreSQL service")
        print("  Windows: net start postgresql-x64-15 (or your version)")
        print("  Linux/Mac: sudo systemctl start postgresql")
        return

    # Test 2: Check connection with postgres user
    success, output, error = run_command('psql -h 127.0.0.1 -p 5432 -U postgres -c "SELECT version();"',
                                        "Test 2: Test connection as postgres user")

    if not success:
        print("\n❌ Cannot connect as postgres user.")
        print("This might indicate PostgreSQL authentication issues.")
        return

    # Test 3: Check if admin_user exists
    success, output, error = run_command(f'psql -h 127.0.0.1 -p 5432 -U postgres -c "SELECT usename FROM pg_user WHERE usename = \'{db_user}\';"',
                                        f"Test 3: Check if user '{db_user}' exists")

    if not success or db_user not in output:
        print(f"\n❌ User '{db_user}' does not exist in PostgreSQL.")
        print("Solution: Create the user")
        print(f"  psql -U postgres -c \"CREATE USER {db_user} WITH PASSWORD '{db_password}';\"")
        return

    # Test 4: Test connection as admin_user
    success, output, error = run_command(f'psql -h 127.0.0.1 -p 5432 -U {db_user} -c "SELECT current_user;"',
                                        f"Test 4: Test connection as '{db_user}'")

    if not success:
        print("\n❌ Cannot connect as user '{db_user}'.")
        print("This indicates a password mismatch.")
        print("\nPossible solutions:")
        print("1. Update password in PostgreSQL:")
        print(f"   psql -U postgres -c \"ALTER USER {db_user} PASSWORD '{db_password}';\"")
        print("2. Or update .env.staging with the correct password")
        return

    # Test 5: Check if database exists
    success, output, error = run_command(f'psql -h 127.0.0.1 -p 5432 -U postgres -c "SELECT datname FROM pg_database WHERE datname = \'{db_name}\';"',
                                        f"Test 5: Check if database '{db_name}' exists")

    if not success or db_name not in output:
        print(f"\n❌ Database '{db_name}' does not exist.")
        print("Solution: Create the database")
        print(f"  psql -U postgres -c \"CREATE DATABASE {db_name} OWNER {db_user};\"")
        return

    # Test 6: Test full connection to staging database
    success, output, error = run_command(f'psql -h 127.0.0.1 -p 5432 -U {db_user} -d {db_name} -c "SELECT current_database(), current_user;"',
                                        f"Test 6: Test full connection to '{db_name}' database")

    if success:
        print("\n✅ All database connection tests passed!")
        print("The staging database is ready for Django.")
    else:
        print(f"\n❌ Cannot connect to database '{db_name}' as user '{db_user}'.")
        print("Check database permissions.")

if __name__ == '__main__':
    main()
