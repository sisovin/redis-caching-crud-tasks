from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    
    def ready(self):
        """
        Initialize signal connections when the app is ready.
        """
        try:
            import accounts.signals  # noqa
        except ImportError:
            pass