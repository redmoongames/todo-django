from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone


class Tag(models.Model):
    name = models.CharField(max_length=50)
    color = models.CharField(
        max_length=7,
        default="#000000",
        validators=[
            RegexValidator(
                regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                message='Color must be a valid hex color code'
            )
        ]
    )
    dashboard = models.ForeignKey('Dashboard', on_delete=models.CASCADE, related_name="tags")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['name', 'dashboard']
        
    def __str__(self) -> str:
        return self.name
    
    def clean(self) -> None:
        if not self.name.strip():
            raise ValidationError("Tag name cannot be empty")