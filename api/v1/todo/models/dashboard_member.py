from django.db import models
from django.contrib.auth.models import User


class DashboardMember(models.Model):
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('editor', 'Editor'),
        ('viewer', 'Viewer'),
    ]
    
    dashboard = models.ForeignKey('Dashboard', on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="dashboard_memberships")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['dashboard', 'user']
        
    def __str__(self) -> str:
        return f"{self.user.username} - {self.dashboard.title} ({self.role})"

