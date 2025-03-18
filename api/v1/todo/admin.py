from django.contrib import admin
from .models.models import Tag, Dashboard, DashboardMember, Todo

admin.site.register(Tag)
admin.site.register(Dashboard)
admin.site.register(DashboardMember)
admin.site.register(Todo)
