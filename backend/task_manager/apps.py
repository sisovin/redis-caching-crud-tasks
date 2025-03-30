from django.apps import AppConfig

class TaskManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'task_manager'
    
    def ready(self):
        try:
            import task_manager.signals  # noqa
        except ImportError:
            pass