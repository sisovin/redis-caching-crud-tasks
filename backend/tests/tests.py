from django.test import TestCase
from django.urls import reverse
from django.core.cache import cache
import redis
from django.conf import settings
import json
from .models import Task  # Use the relative import here as we're in the app directory

# Configure Redis connection
redis_client = redis.StrictRedis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB
)

class RedisCachingTests(TestCase):

    def setUp(self):
        self.task = Task.objects.create(title="Test Task", description="Test Description", completed=False)
        cache.clear()
        redis_client.flushdb()  # Clear Redis cache before each test

    def test_cache_task(self):
        self.task.cache_task()
        cache_key = f"task_{self.task.id}"
        cached_task = redis_client.get(cache_key)
        self.assertIsNotNone(cached_task)
        self.assertEqual(json.loads(cached_task), self.task.to_dict())

    def test_uncache_task(self):
        self.task.cache_task()
        self.task.uncache_task()
        cache_key = f"task_{self.task.id}"
        cached_task = redis_client.get(cache_key)
        self.assertIsNone(cached_task)

    def test_get_cached_task(self):
        task_dict = Task.get_cached_task(self.task.id)
        self.assertEqual(task_dict, self.task.to_dict())

    def test_get_tasks(self):
        response = self.client.get(reverse('get_tasks'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_create_task(self):
        # Send JSON data instead of form data
        data = {
            'title': 'New Task',
            'description': 'New Description',
            'completed': False
        }
        response = self.client.post(
            reverse('create_task'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'Task created')

    def test_update_task(self):
        # Send JSON data instead of form data
        data = {
            'title': 'Updated Task',
            'description': 'Updated Description'
        }
        response = self.client.put(
            reverse('update_task', args=[self.task.id]),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'Task updated')

    def test_delete_task(self):
        response = self.client.delete(reverse('delete_task', args=[self.task.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'Task deleted')

    def test_frequently_accessed_data(self):
        response = self.client.get(reverse('frequently_accessed_data'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('data', response.json())