# Generated by Django 5.1.7 on 2025-03-18 22:00

import django.core.validators
import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Dashboard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('is_public', models.BooleanField(default=False)),
                ('public_link', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owned_dashboards', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('color', models.CharField(default='#000000', max_length=7, validators=[django.core.validators.RegexValidator(message='Color must be a valid hex color code', regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('dashboard', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tags', to='api.dashboard')),
            ],
            options={
                'unique_together': {('name', 'dashboard')},
            },
        ),
        migrations.CreateModel(
            name='Todo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('priority', models.IntegerField(choices=[(1, 'Very Low'), (2, 'Low'), (3, 'Medium'), (4, 'High'), (5, 'Very High')], default=3)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('due_date', models.DateField(blank=True, null=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('completed', 'Completed')], default='pending', max_length=10)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('completed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='completed_todos', to=settings.AUTH_USER_MODEL)),
                ('dashboard', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='todos', to='api.dashboard')),
                ('tags', models.ManyToManyField(blank=True, related_name='todos', to='api.tag')),
            ],
        ),
        migrations.CreateModel(
            name='DashboardMember',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('owner', 'Owner'), ('editor', 'Editor'), ('viewer', 'Viewer')], max_length=10)),
                ('joined_at', models.DateTimeField(auto_now_add=True)),
                ('dashboard', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='members', to='api.dashboard')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dashboard_memberships', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('dashboard', 'user')},
            },
        ),
    ]
