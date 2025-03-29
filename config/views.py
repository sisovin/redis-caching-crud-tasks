import json
import redis
from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from task_manager.models import Task  # Using absolute import

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
            return JsonResponse(json.loads(cached_result))
        result = func(*args, **kwargs)
        redis_client.set(cache_key, json.dumps(result.content.decode()), ex=60*5)  # Cache for 5 minutes
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

@csrf_exempt
@require_http_methods(["POST"])
def create_task(request):
    try:
        data = json.loads(request.body)
        task = Task.objects.create(
            title=data.get('title', ''),
            description=data.get('description', ''),
            completed=data.get('completed', False)
        )
        
        # Cache the individual task
        task_dict = {
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'completed': task.completed
        }
        cache_key = f"task_{task.id}"
        redis_client.set(cache_key, json.dumps(task_dict), ex=60*15)
        
        # Invalidate the tasks list cache
        cache.delete('tasks')
        
        return JsonResponse({'status': 'Task created', 'task_id': task.id})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["PUT"])
def update_task(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
        data = json.loads(request.body)
        
        # Update task fields
        if 'title' in data:
            task.title = data['title']
        if 'description' in data:
            task.description = data['description']
        if 'completed' in data:
            task.completed = data['completed']
        
        task.save()
        
        # Update task in cache
        task_dict = {
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'completed': task.completed
        }
        cache_key = f"task_{task.id}"
        redis_client.set(cache_key, json.dumps(task_dict), ex=60*15)
        
        # Invalidate the tasks list cache
        cache.delete('tasks')
        
        return JsonResponse({'status': 'Task updated', 'task_id': task.id})
    except Task.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Task not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_task(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
        task_id = task.id
        task.delete()
        
        # Remove task from cache
        cache_key = f"task_{task_id}"
        redis_client.delete(cache_key)
        
        # Invalidate the tasks list cache
        cache.delete('tasks')
        
        return JsonResponse({'status': 'Task deleted', 'task_id': task_id})
    except Task.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Task not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@memoize
def frequently_accessed_data(request):
    # Example implementation of frequently accessed data
    data = {
        'data': 'Frequently accessed data',
        'stats': {
            'total_tasks': Task.objects.count(),
            'completed_tasks': Task.objects.filter(completed=True).count()
        }
    }
    return JsonResponse(data)