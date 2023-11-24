from django.contrib import admin
from .models import Task, TaskAssignment

# Register your models here.

admin.site.register(Task)
admin.site.register(TaskAssignment)
