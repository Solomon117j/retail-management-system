import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retail_management_system.settings')
import django
django.setup()
from django.db import connection
cursor = connection.cursor()
cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
tables = cursor.fetchall()
for table in tables:
    cursor.execute(f"DROP TABLE IF EXISTS {table[0]} CASCADE")
print('Dropped all tables')
