import os
import sys
import django
from django.conf import settings

# Clear environment
os.environ.pop('DJANGO_SETTINGS_MODULE', None)
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Configure settings
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
settings.configure(
    INSTALLED_APPS=[
        'django.contrib.contenttypes',
        'django.contrib.auth',
        'store_management',
        'human_resources',
    ],
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
)

# Initialize Django
django.setup()

# Clear app registry cache
from django.apps import apps
apps.models_ready = False
apps.ready = False
apps.clear_cache()
apps.all_models = {}
apps.app_configs = {}
apps.loading = False
apps.populate(settings.INSTALLED_APPS)

# Run migrations
from django.core.management import call_command
try:
    call_command('makemigrations', 'store_management', 'human_resources', interactive=False)
    call_command('migrate', interactive=False)
    print("Migrations completed successfully!")
except Exception as e:
    print(f"Migration error: {e}")
    sys.exit(1)