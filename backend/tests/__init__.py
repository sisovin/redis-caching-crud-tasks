"""
Test package for the Redis Caching CRUD Tasks application.

This package contains tests for both individual components and integration testing
across the entire application. The testing approach uses a combination of Django's
built-in TestCase and pytest for more advanced testing features.

Test Categories:
- Unit tests: Test individual components in isolation
- Integration tests: Test interaction between components
- Caching tests: Specifically test Redis caching functionality
"""

# Import common test utilities
from django.test import TestCase, Client
from rest_framework.test import APIClient, APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.cache import cache

# Import Redis client for cache testing
import redis
from django.conf import settings
import json

# Create a redis client for direct cache testing
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD,
    decode_responses=True
)

# Import core models for testing
from task_manager.models import Task
from accounts.models import User

# Import utility functions to help with testing
from core.cache.utils import get_cache, set_cache, invalidate_cache_prefix

# Test helper functions
def clear_cache():
    """Clear Django and Redis cache for a clean test environment"""
    cache.clear()
    redis_client.flushdb()

def create_test_user(username="testuser", password="password123", email="test@example.com"):
    """Create a test user for authentication tests"""
    User = get_user_model()
    return User.objects.create_user(
        username=username,
        password=password,
        email=email
    )

def create_test_task(user, title="Test Task", description="Test Description", completed=False):
    """Create a test task for task-related tests"""
    return Task.objects.create(
        user=user,
        title=title,
        description=description,
        completed=completed
    )

def get_auth_client(user):
    """Get an authenticated API client for the given user"""
    client = APIClient()
    client.force_authenticate(user=user)
    return client