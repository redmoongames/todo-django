from django.urls import path
from .views import (
    DashboardCollectionView, DashboardDetailView,
    TodoCollectionView, TodoDetailView, TodoActionView, TodoSearchView,
    TagCollectionView, TagDetailView,
    MemberCollectionView, MemberDetailView
)

app_name = 'todo'

urlpatterns = [
    # GET POST
    path('dashboards/', DashboardCollectionView.as_view(), name='dashboard-collection'),

    # GET PUT DELETE
    path('dashboards/<int:dashboard_id>/', DashboardDetailView.as_view(), name='dashboard-detail'),

    # GET POST
    path('dashboards/<int:dashboard_id>/todos/', TodoCollectionView.as_view(), name='todo-collection'),

    # GET PUT DELETE
    path('dashboards/<int:dashboard_id>/todos/<int:todo_id>/', TodoDetailView.as_view(), name='todo-detail'),

    # POST
    path('dashboards/<int:dashboard_id>/todos/<int:todo_id>/<str:action>/', TodoActionView.as_view(), name='todo-action'),

    # GET
    path('dashboards/<int:dashboard_id>/todos/search/', TodoSearchView.as_view(), name='todo-search'),

    # GET POST
    path('dashboards/<int:dashboard_id>/tags/', TagCollectionView.as_view(), name='tag-collection'),

    # GET PUT DELETE
    path('dashboards/<int:dashboard_id>/tags/<int:tag_id>/', TagDetailView.as_view(), name='tag-detail'),
    
    # GET POST - List all members and add a new member
    path('dashboards/<int:dashboard_id>/members/', MemberCollectionView.as_view(), name='member-collection'),
    
    # PUT DELETE - Update or remove a member
    path('dashboards/<int:dashboard_id>/members/<int:member_id>/', MemberDetailView.as_view(), name='member-detail'),
] 