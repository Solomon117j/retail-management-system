# accounts/apps.py
from django.apps import AppConfig
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)


def safe_update_last_login(sender, user, request, **kwargs):
    """Safely update last_login by using a queryset update to avoid Model.save(update_fields) issues and skip post_save signals."""
    try:
        UserModel = user.__class__
        # Use update() to avoid calling Model.save() and triggering signals
        updated = UserModel.objects.filter(pk=user.pk).update(last_login=timezone.now())
        if not updated:
            logger.warning(f"No rows updated for last_login of user {getattr(user, 'username', user)} (pk={user.pk})")
    except Exception as e:
        logger.error(f"Failed to update last_login for {getattr(user, 'username', user)}: {e}")


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        # This will show in test output if signals are loaded
        print("!!! AccountsConfig ready() called - signals should be loaded !!!")
        import accounts.signals  # noqa: F401

        # Import here to avoid AppRegistryNotReady during app loading
        from django.contrib.auth.signals import user_logged_in
        from django.contrib.auth.models import update_last_login

        # Work around DatabaseError: "Save with update_fields did not affect any rows"
        # by replacing Django's default last_login updater with a safer version.
        try:
            # Prefer disconnecting by receiver reference
            user_logged_in.disconnect(receiver=update_last_login)
        except Exception as e:
            logger.debug(f"Could not disconnect default update_last_login by receiver: {e}")
            try:
                # Fallback: attempt by dispatch_uid if any
                user_logged_in.disconnect(dispatch_uid="update_last_login")
            except Exception as e2:
                logger.debug(f"Could not disconnect default update_last_login by dispatch_uid: {e2}")

        # Ensure our handler is connected exactly once
        try:
            user_logged_in.disconnect(receiver=safe_update_last_login)
        except Exception:
            pass
        user_logged_in.connect(safe_update_last_login, dispatch_uid="accounts.safe_update_last_login")