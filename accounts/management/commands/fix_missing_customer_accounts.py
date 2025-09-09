from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from e_commerce.models import CustomerAccount
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class Command(BaseCommand):
    help = 'Create missing CustomerAccount entries for users with is_customer=True'

    def handle(self, *args, **options):
        users = User.objects.filter(is_customer=True)
        created_count = 0
        for user in users:
            try:
                if not CustomerAccount.objects.filter(user=user).exists():
                    CustomerAccount.objects.create(
                        user=user,
                        first_name=getattr(user, 'first_name', '') or '',
                        last_name=getattr(user, 'last_name', '') or '',
                        email=user.email or ''
                    )
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f'Created CustomerAccount for user {user.username}'))
            except Exception as e:
                logger.error(f'Error creating CustomerAccount for user {user.username}: {e}')
                self.stdout.write(self.style.ERROR(f'Error creating CustomerAccount for user {user.username}: {e}'))
        self.stdout.write(self.style.SUCCESS(f'Total CustomerAccounts created: {created_count}'))
