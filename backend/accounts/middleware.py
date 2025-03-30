from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin

class UserActivityMiddleware(MiddlewareMixin):
    """
    Middleware to track user's last activity time.
    Updates the last_activity field for authenticated users.
    """
    
    def process_request(self, request):
        """
        Process each request to update the user's last activity timestamp.
        Only updates periodically to avoid excessive database writes.
        """
        if request.user.is_authenticated:
            # Get last activity time
            last_activity = getattr(request.user, 'last_activity', None)
            
            # If no last activity or it was more than 15 minutes ago, update it
            if not last_activity or (timezone.now() - last_activity).seconds > 900:
                request.user.mark_active()