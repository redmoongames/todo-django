from django.urls import path
from . import views_tasks
from . import views_auth
from . import views_labels
from . import views_health

urlpatterns = [
    path('health/', views_health.health_check, name='health_check'),
    # Auth endpoints
    path('auth/register/', views_auth.register, name='register'),
    path('auth/login/', views_auth.login_view, name='login'),
    path('auth/logout/', views_auth.logout_view, name='logout'),
    path('auth/verify/', views_auth.verify_token_view, name='verify_token'),
    path('auth/refresh/', views_auth.refresh_token_view, name='refresh_token'),
    
    # Task endpoints
    path('tasks/', views_tasks.task_items, name='task_list'),
    path('tasks/<int:id>/', views_tasks.task_item_by_id, name='task_detail'),
    
    # Label endpoints
    path('labels/', views_labels.labels, name='label_list'),
    path('labels/<int:id>/', views_labels.label_detail, name='label_detail'),
]
