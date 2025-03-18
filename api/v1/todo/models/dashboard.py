from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
from typing import Any


class Dashboard(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_dashboards")
    is_public = models.BooleanField(default=False)
    public_link = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return self.title


@receiver(post_save, sender=Dashboard)
def create_owner_member(sender: type[Dashboard], instance: Dashboard, created: bool, **kwargs: Any) -> None:
    if created:
        from .dashboard_member import DashboardMember
        DashboardMember.objects.create(
            dashboard=instance,
            user=instance.owner,
            role='owner'
        )
