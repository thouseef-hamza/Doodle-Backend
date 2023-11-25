from ..models import Task, TaskAssignment
from rest_framework import serializers
from accounts.models import User
from django.db.models import Q
from institutes.models import Batch
import logging

logger = logging.getLogger(__name__)


# For Creating Task
class InstituteTaskCreateSerializer(serializers.ModelSerializer):
    assigned_to = serializers.ListField()

    class Meta:
        model = Task
        fields = "__all__"
        read_only_fields = (
            "id",
            "created_at",
        )
        extra_kwargs = {
            "assigned_by": {"required": False},
            "user_type": {"required": False},
        }

    def validate_title(self, value):
        return value.title()

# For Listing, and Getting Task
class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        exclude = ("assigned_by", "user_type")

            

# For Inheriting
class UserTaskSerializer(serializers.ModelSerializer):
    unique_code = serializers.CharField(read_only=True)
    batch_name = serializers.CharField(read_only=True)

    # institute=serializers.CharField()
    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "unique_code", "email", "batch_name")


# For Deserialization for Get Request
class TaskAssignmentSerializer(serializers.ModelSerializer):
    user = UserTaskSerializer(read_only=True)

    class Meta:
        model = TaskAssignment
        exclude = ("task",)
        read_only_fields=("id","task_id","user_id")
