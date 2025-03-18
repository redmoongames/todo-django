from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import date


class Todo(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    ]
    
    PRIORITY_CHOICES = [
        (1, 'Very Low'),
        (2, 'Low'),
        (3, 'Medium'),
        (4, 'High'),
        (5, 'Very High'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=3)
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    dashboard = models.ForeignKey('Dashboard', on_delete=models.CASCADE, related_name="todos")
    tags = models.ManyToManyField('Tag', blank=True, related_name="todos")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    completed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="completed_todos")
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self) -> str:
        return self.title
    
    def clean(self) -> None:
        if not self.title.strip():
            raise ValidationError("Todo title cannot be empty")
            
        if self.due_date and self.due_date < date.today():
            raise ValidationError("Due date cannot be in the past")
    
    def complete(self, user: User) -> None:
        if self.status == 'completed':
            raise ValidationError("Todo is already completed")
            
        self.status = 'completed'
        self.completed_by = user
        self.completed_at = timezone.now()
        self.save()
    
    def uncomplete(self) -> None:
        if self.status == 'pending':
            raise ValidationError("Todo is already pending")
            
        self.status = 'pending'
        self.completed_by = None
        self.completed_at = None
        self.save()
