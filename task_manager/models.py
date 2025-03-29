from django.db import models
import redis
import json
from django.conf import settings

# Configure Redis connection
redis_client = redis.StrictRedis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB
)

class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    completed = models.BooleanField(default=False)

    class Meta:
        app_label = 'task_manager'

    def __str__(self):
        return self.title

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "completed": self.completed
        }

    def cache_task(self):
        cache_key = f"task_{self.id}"
        # Use json.dumps instead of str() to ensure valid JSON
        redis_client.set(cache_key, json.dumps(self.to_dict()), ex=60*15)  # Cache for 15 minutes

    def uncache_task(self):
        cache_key = f"task_{self.id}"
        redis_client.delete(cache_key)

    @classmethod
    def get_cached_task(cls, task_id):
        cache_key = f"task_{task_id}"
        cached_task = redis_client.get(cache_key)
        if cached_task:
            # Use json.loads to properly parse the JSON string
            return json.loads(cached_task.decode('utf-8'))
        task = cls.objects.get(id=task_id)
        task.cache_task()
        return task.to_dict()