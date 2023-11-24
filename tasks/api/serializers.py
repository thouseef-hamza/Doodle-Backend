from ..models import Task, TaskAssignment
from rest_framework import serializers
from accounts.models import User
from django.db.models import Q
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

    # Pending .................................
    def update(self, instance, validated_data):
        print(instance.task_type)
        assigned_to = validated_data.pop("assigned_to")
        print(assigned_to)
        instance.title = validated_data.get("title", instance.title)
        instance.description = validated_data.get("description", instance.description)
        instance.task_type = validated_data.get("task_type", instance.task_type)
        instance.task_url = validated_data.get("task_url", instance.task_url)
        instance.document = validated_data.get("document", instance.document)
        instance.due_date = validated_data.get("due_date", instance.due_date)
        Q_filter = Q()
        print(instance.task_type, "ghgghgjjjjjjjjj")
        if instance.task_type == "individual":
            print("ygf")
            Q_filter |= Q(id__in=assigned_to)
        elif instance.task_type == "teacher":
            Q_filter |= Q(email=assigned_to[0])
        elif instance.task_type == "batch":
            Q_filter |= Q(student_profile__batch__id__in=assigned_to)
        print(Q_filter)
        users = User.objects.filter(Q_filter).values_list("id", flat=True)
        print(*users)
        print()
        instance.assigned_to.set([user for user in users])
        instance.save()
        return instance


# For Listing, and Getting Task
class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        exclude = ("assigned_by", "user_type")


# For Inheriting
class UserTaskSerializer(serializers.ModelSerializer):
    unique_code = serializers.CharField()

    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "unique_code", "email")


# For Deserialization for Get Request
class TaskAssignmentSerializer(serializers.ModelSerializer):
    user = UserTaskSerializer(read_only=True)

    class Meta:
        model = TaskAssignment
        exclude = ("task",)
