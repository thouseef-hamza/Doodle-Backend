from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.models import User
from .api.serializers import (
    UserStudentSerializer,
    UserStudentProfileUpdateSerializer,
    UserStudentTaskAssignmentSerializer,
)
from tasks.models import TaskAssignment, Task
from django.db.models import F


class UserStudentUpdateAPIView(APIView):
    def get_queryset(self, user_id):
        return User.objects.filter(id=user_id).select_related("student_profile").first()

    def get(self, request, *args, **kwargs):
        instance = self.get_queryset(request.user.id)
        if not instance:
            return Response({"msg": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserStudentSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        instance = self.get_queryset(request.user.id)
        if not instance:
            return Response({"msg": "User Not Found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserStudentProfileUpdateSerializer(instance, request.data)
        if serializer.is_valid():
            instance.first_name = serializer.validated_data.get(
                "first_name", instance.first_name
            )
            instance.last_name = serializer.validated_data.get(
                "last_name", instance.last_name
            )
            instance.email = serializer.validated_data.get("email", instance.email)
            instance.phone_number = serializer.validated_data.get(
                "phone_number", instance.phone_number
            )
            profile_data = serializer.validated_data.pop("profile")
            instance.student_profile.gender = profile_data.get(
                "gender", instance.student_profile.gender
            )
            instance.student_profile.date_of_birth = profile_data.get(
                "date_of_birth", instance.student_profile.date_of_birth
            )
            instance.student_profile.profile_picture = profile_data.get(
                "profile_picture", instance.student_profile.profile_picture
            )
            instance.student_profile.address = profile_data.get(
                "address", instance.student_profile.address
            )
            instance.student_profile.city = profile_data.get(
                "city", instance.student_profile.city
            )
            instance.student_profile.state = profile_data.get(
                "state", instance.student_profile.state
            )
            instance.student_profile.postal_code = profile_data.get(
                "postal_code", instance.student_profile.postal_code
            )
            instance.student_profile.save()
            instance.save(
                update_fields=["first_name", "last_name", "email", "phone_number"]
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        # When student tries to delete institute gets notification
        # He will decide whether approve or not
        pass


class UserStudentTaskRetrieveListAPIView(APIView):
    def get(self, request, *args, **kwargs):
        instance = Task.objects.filter(assigned_to=request.user.id).values()
        return Response(instance, status=status.HTTP_200_OK)


class UserStudentTaskAssignmentRetrieveUpdateAPIView(APIView):
    def get_queryset(self, task_id, user):
        return TaskAssignment.objects.filter(task_id=id, user_id=user.id)

    def get(self, request, pk=None, *args, **kwargs):
        instance = (
            self.get_queryset(task_id=pk, user=request.user)
            .select_related("task")
            .values(
                "id",
                "task_id",
                "submitted_url",
                "submitted_document",
                "submitted_url",
                "feedback",
                "is_submitted",
                "is_completed",
                task_title=F("task__title"),
                task_description=F("task__description"),
                assigned_by=F("task__assigned_by"),
                task_url=F("task__task_url"),
                document=F("task__document"),
                due_date=F("task__due_date"),
                created_at=F("task__created_at"),
            )
        )
        return Response(instance, status=status.HTTP_200_OK)

    def put(self, request, pk=None, *args, **kwargs):
        instance = self.get_queryset(task_id=pk, user=request.user.id).first()
        serializer = UserStudentTaskAssignmentSerializer(data=request.data)
        if serializer.is_valid():
            instance.submitted_url = serializer.validated_data.get(
                "submitted_url", instance.submitted_url
            )
            instance.submitted_document = serializer.validated_data.get(
                "submitted_document", instance.submitted_document
            )
            instance.feedback = serializer.validated_data.get(
                "feedback", instance.feedback
            )
            instance.save(
                update_fields=["submitted_url", "submitted_document", "feedback"]
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_200_OK)
