
from django.urls import path, include

urlpatterns = [
    path('auth/', include('api.v1.auth.urls')),
    path('todo/', include('api.v1.todo.urls')),
]
