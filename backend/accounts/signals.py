from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from core.cache.utils import invalidate_cache_prefix

User = get_user_model()

@receiver(post_save, sender=User)
def user_saved(sender, instance, created, **kwargs):
    """
    Signal handler for user model saves.
    Invalidates user-related cache when a user is created or updated.
    """
    # Invalidate specific user cache
    invalidate_cache_prefix(f'user-detail:{instance.pk}')
    invalidate_cache_prefix(f'user-profile:{instance.pk}')
    
    # Invalidate list caches
    invalidate_cache_prefix('user-list')

@receiver(post_delete, sender=User)
def user_deleted(sender, instance, **kwargs):
    """
    Signal handler for user model deletions.
    Invalidates user-related cache when a user is deleted.
    """
    # Invalidate list caches
    invalidate_cache_prefix('user-list')