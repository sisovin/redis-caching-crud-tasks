import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from task_manager.models import Task
from core.cache.utils import get_cache, set_cache

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_task():
    def _create_task(title, description, completed=False):
        return Task.objects.create(title=title, description=description, completed=completed)
    return _create_task

@pytest.mark.django_db
def test_task_list_caching(api_client, create_task):
    url = reverse('task-list')
    create_task('Task 1', 'Description 1')
    create_task('Task 2', 'Description 2')

    # First request to populate cache
    response = api_client.get(url)
    assert response.status_code == 200
    assert len(response.data) == 2

    # Check if cache is set
    cache_key = 'task_list'
    cached_data = get_cache(cache_key)
    assert cached_data is not None

    # Second request to get data from cache
    response = api_client.get(url)
    assert response.status_code == 200
    assert len(response.data) == 2

@pytest.mark.django_db
def test_task_retrieve_caching(api_client, create_task):
    task = create_task('Task 1', 'Description 1')
    url = reverse('task-detail', args=[task.id])

    # First request to populate cache
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.data['title'] == 'Task 1'

    # Check if cache is set
    cache_key = f'task_detail:{task.id}'
    cached_data = get_cache(cache_key)
    assert cached_data is not None

    # Second request to get data from cache
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.data['title'] == 'Task 1'