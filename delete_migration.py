import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retail_management_system.settings')

django.setup()

from django.db import connection

cursor = connection.cursor()

cursor.execute("DELETE FROM django_migrations WHERE app = 'e_commerce' AND name IN ('0002_initial', '0003_cart_cartitem', '0004_customeraccount_marketing_opt_in_and_more', '0005_remove_cartitem_unique_cart_product_and_more')")

print('Deleted migration records')
