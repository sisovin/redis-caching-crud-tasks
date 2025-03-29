import redis
from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_http_methods
from .models import Task

# Configure Redis connection
redis_client = redis.StrictRedis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB
)

# Memoization decorator
def memoize(func):
    def wrapper(*args, **kwargs):
        cache_key = f"{func.__name__}_{args}_{kwargs}"
        cached_result = redis_client.get(cache_key)
        if cached_result:
            return JsonResponse(eval(cached_result))
        result = func(*args, **kwargs)
        redis_client.set(cache_key, str(result), ex=60*5)  # Cache for 5 minutes
        return result
    return wrapper

@require_http_methods(["GET"])
@cache_page(60 * 15)  # Cache page for 15 minutes
def get_tasks(request):
    tasks = cache.get('tasks')
    if not tasks:
        tasks = list(Task.objects.all().values())
        cache.set('tasks', tasks, timeout=60*15)  # Cache for 15 minutes
    return JsonResponse(tasks, safe=False)

@require_http_methods(["POST"])
def create_task(request):
    # Invalidate cache
    cache.delete('tasks')
    # Create task logic
    # ...
    return JsonResponse({'status': 'Task created'})

@require_http_methods(["PUT"])
def update_task(request, task_id):
    # Invalidate cache
    cache.delete('tasks')
    # Update task logic
    # ...
    return JsonResponse({'status': 'Task updated'})

@require_http_methods(["DELETE"])
def delete_task(request, task_id):
    # Invalidate cache
    cache.delete('tasks')
    # Delete task logic
    # ...
    return JsonResponse({'status': 'Task deleted'})

@memoize
def frequently_accessed_data(request):
    # Logic to retrieve frequently accessed data
    # ...
    return JsonResponse({'data': 'Frequently accessed data'})
