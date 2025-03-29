from django.urls import path
from .views import get_tasks, create_task, update_task, delete_task, frequently_accessed_data

urlpatterns = [
    path('tasks/', get_tasks, name='get_tasks'),
    path('tasks/create/', create_task, name='create_task'),
    path('tasks/update/<int:task_id>/', update_task, name='update_task'),
    path('tasks/delete/<int:task_id>/', delete_task, name='delete_task'),
    path('frequently-accessed-data/', frequently_accessed_data, name='frequently_accessed_data'),
]
