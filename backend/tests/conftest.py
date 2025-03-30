import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.core.cache import cache
import redis
from django.conf import settings
from task_manager.models import Task

User = get_user_model()

@pytest.fixture(scope="function")
def api_client():
    """Return an API client for testing API endpoints."""
    return APIClient()

@pytest.fixture(scope="function")
def authenticated_client(test_user):
    """Return an authenticated API client."""
    client = APIClient()
    client.force_authenticate(user=test_user)
    return client

@pytest.fixture(scope="function")
def admin_client(admin_user):
    """Return an API client authenticated as admin."""
    client = APIClient()
    client.force_authenticate(user=admin_user)
    return client

@pytest.fixture(scope="function")
def test_user():
    """Create and return a test user."""
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpassword123'
    )
    return user

@pytest.fixture(scope="function")
def admin_user():
    """Create and return an admin user."""
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123'
    )
    return admin

@pytest.fixture(scope="function")
def test_tasks(test_user):
    """Create and return a set of test tasks."""
    tasks = []
    for i in range(3):
        task = Task.objects.create(
            title=f"Test Task {i}",
            description=f"Test Description {i}",
            user=test_user,
            priority=i % 3 + 1,
            status='pending' if i < 2 else 'completed',
            completed=(i >= 2)
        )
        tasks.append(task)
    return tasks

@pytest.fixture(scope="function")
def redis_client():
    """Return a Redis client for direct cache testing."""
    return redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        password=settings.REDIS_PASSWORD,
        decode_responses=True
    )

@pytest.fixture(autouse=True)
def clear_cache():
    """Clear the cache before and after each test."""
    # Clear cache before test
    cache.clear()
    # Run the test
    yield
    # Clear cache after test
    cache.clear()

@pytest.fixture(scope="function")
def cache_key_prefix():
    """Return a unique cache key prefix for testing."""
    import uuid
    return f"test:{uuid.uuid4()}"

@pytest.fixture(scope="function")
def mock_redis(monkeypatch):
    """Mock Redis for isolated testing without actual Redis server."""
    class MockRedis:
        def __init__(self):
            self.data = {}
            self.expires = {}
        
        def get(self, key):
            return self.data.get(key)
            
        def set(self, key, value, ex=None):
            self.data[key] = value
            if ex:
                self.expires[key] = ex
            return True
            
        def delete(self, *keys):
            count = 0
            for key in keys:
                if key in self.data:
                    del self.data[key]
                    count += 1
            return count
            
        def flushdb(self):
            self.data = {}
            self.expires = {}
            return True
            
        def keys(self, pattern="*"):
            import fnmatch
            return [k for k in self.data.keys() if fnmatch.fnmatch(k, pattern)]
            
        def scan(self, cursor=0, match=None, count=None):
            if cursor == 0:
                keys = self.keys(match) if match else list(self.data.keys())
                return (1, keys[:count]) if count and count < len(keys) else (0, keys)
            return (0, [])
    
    mock_inst = MockRedis()
    
    # Patch redis.Redis to return our mock
    monkeypatch.setattr(redis, "Redis", lambda **kwargs: mock_inst)
    
    # Patch Django's cache
    from django_redis.client.default import DefaultClient
    monkeypatch.setattr(DefaultClient, "get_client", lambda self, *args, **kwargs: mock_inst)
    
    return mock_inst