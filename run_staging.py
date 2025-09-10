#!/usr/bin/env python
"""
Script to run Django development server in staging environment.
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    # Add the project directory to the Python path
    project_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(project_dir))

    # Set the Django settings module for staging
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retail_management_system.settings_staging')

    # Load staging environment variables
    env_file = project_dir / '.env.staging'
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv(env_file)
        print("Loaded staging environment variables from .env.staging")
    else:
        print("Warning: .env.staging file not found. Using default environment variables.")

    # Run the Django development server
    try:
        from django.core.management import execute_from_command_line
        print("Starting Django development server in STAGING mode...")
        print("Environment: STAGING")
        print("Settings module: retail_management_system.settings_staging")
        print("Press Ctrl+C to stop the server")
        print("-" * 50)

        # Execute the runserver command
        execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8000'])

    except KeyboardInterrupt:
        print("\nServer stopped by user.")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
