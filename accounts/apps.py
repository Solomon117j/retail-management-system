# accounts/apps.py
from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        # This will show in test output if signals are loaded
        print("!!! AccountsConfig ready() called - signals should be loaded !!!")
        import accounts.signals