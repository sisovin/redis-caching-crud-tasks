from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """
    Custom User model that extends Django's built-in AbstractUser.
    
    This allows for easy extension of the user model in the future
    without having to change database schemas.
    """
    # Example of adding custom fields
    bio = models.TextField(blank=True, verbose_name=_("Biography"))
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name=_("Avatar"))
    
    # User preferences
    enable_notifications = models.BooleanField(default=True, verbose_name=_("Enable notifications"))
    
    # Meta
    last_activity = models.DateTimeField(null=True, blank=True, verbose_name=_("Last activity"))
    
    # Fix the related_name conflicts
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        help_text=_('The groups this user belongs to.'),
        related_name='accounts_user_set',  # Custom related_name
        related_query_name='user',
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name='accounts_user_set',  # Custom related_name
        related_query_name='user',
    )
    
    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        
    def __str__(self):
        return self.username
    
    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        If both fields are empty, returns the username.
        """
        full_name = super().get_full_name()
        return full_name if full_name else self.username
    
    def mark_active(self):
        """
        Update the user's last activity timestamp.
        """
        from django.utils import timezone
        self.last_activity = timezone.now()
        self.save(update_fields=['last_activity'])