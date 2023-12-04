from django.db import models
from accounts.models import User
from django.conf import settings
from datetime import datetime, timedelta

# Create your models here.


class Task(models.Model):
    class UserType(models.TextChoices):
        TEACHER = "teacher", "Teacher"
        INSTITUTE = "institute", "Institute"

    class TaskType(models.TextChoices):
        INDIVIDUAL = "individual", "Individual"
        BATCH = "batch", "Batch"
        TEACHER = "teacher", "Teacher"

    title = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    assigned_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="task_assigned_by"
    )
    assigned_to = models.ManyToManyField(
        User, related_name="task_assigned_to", through="TaskAssignment"
    )
    user_type = models.CharField(max_length=20, choices=UserType.choices)
    task_type = models.CharField(max_length=20, choices=TaskType.choices)
    task_url = models.URLField(null=True, blank=True)
    document = models.FileField(upload_to="task_documents/", null=True, blank=True)
    due_date = models.DateField(default=datetime.now().date() + timedelta(days=3))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class TaskAssignment(models.Model):
    class TaskAssignmentStatus(models.TextChoices):
        GOOD = "good", "Good"
        FAIR = "fair", "Fair"
        NEEDS_IMPROVEMENT = "needs_improvement", "Needs Improvement"
        REVIEWING = "reviewing", "Reviewing"

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True)
    submitted_url = models.URLField(null=True, blank=True)
    submitted_document = models.FileField(
        upload_to="task_documents/", null=True, blank=True
    )
    status = models.CharField(
        max_length=20,
        choices=TaskAssignmentStatus.choices,
        default=TaskAssignmentStatus.REVIEWING,
    )
    feedback = models.TextField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    is_submitted = models.BooleanField(default=False)

    def __str__(self):
        return (
            f"{self.task.title.upper()} - {self.task.assigned_by} ({self.task.user_type}) to {self.user}"
            if self.task
            else str(self.user)
        )
