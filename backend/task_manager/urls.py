from django.urls import path
from .views import (
    get_tasks,
    create_task,
    update_task,
    delete_task,
    frequently_accessed_data
)

urlpatterns = [
    path('', get_tasks, name='get-tasks'),
    path('create/', create_task, name='create-task'),
    path('update/<int:task_id>/', update_task, name='update-task'),
    path('delete/<int:task_id>/', delete_task, name='delete-task'),
    path('frequently-accessed-data/', frequently_accessed_data, name='frequently-accessed-data'),
]