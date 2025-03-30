import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from task_manager.models import Task
from accounts.models import User

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_task():
    def _create_task(title, description, completed=False):
        return Task.objects.create(title=title, description=description, completed=completed)
    return _create_task

@pytest.fixture
def create_user():
    def _create_user(username, password, email):
        return User.objects.create_user(username=username, password=password, email=email)
    return _create_user

@pytest.mark.django_db
def test_task_crud_operations(api_client, create_task):
    # Create task
    url = reverse('task-list')
    data = {'title': 'Task 1', 'description': 'Description 1'}
    response = api_client.post(url, data)
    assert response.status_code == 201
    assert response.data['title'] == 'Task 1'

    # Retrieve task
    task_id = response.data['id']
    url = reverse('task-detail', args=[task_id])
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.data['title'] == 'Task 1'

    # Update task
    data = {'title': 'Updated Task 1'}
    response = api_client.put(url, data)
    assert response.status_code == 200
    assert response.data['title'] == 'Updated Task 1'

    # Delete task
    response = api_client.delete(url)
    assert response.status_code == 204

@pytest.mark.django_db
def test_user_crud_operations(api_client, create_user):
    # Create user
    url = reverse('user-list')
    data = {'username': 'user1', 'password': 'password123', 'email': 'user1@example.com'}
    response = api_client.post(url, data)
    assert response.status_code == 201
    assert response.data['username'] == 'user1'

    # Retrieve user
    user_id = response.data['id']
    url = reverse('user-detail', args=[user_id])
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.data['username'] == 'user1'

    # Update user
    data = {'username': 'updated_user1'}
    response = api_client.put(url, data)
    assert response.status_code == 200
    assert response.data['username'] == 'updated_user1'

    # Delete user
    response = api_client.delete(url)
    assert response.status_code == 204