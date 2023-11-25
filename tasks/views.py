from django.shortcuts import render
from rest_framework.views import APIView
from .models import Task, TaskAssignment
from .api.serializers import (
    InstituteTaskCreateSerializer,
    TaskSerializer,
    TaskAssignmentSerializer,
)
from rest_framework.response import Response
from rest_framework import status
from accounts.models import User
from django.db.models import Q, F
from rest_framework.permissions import IsAuthenticated
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema

# Create your views here.


class InstituteTaskListCreateAPIView(APIView):
    @swagger_auto_schema(
        tags=["Institute  Task"],
        operation_description="Institute Task List",
        responses={
            200: TaskSerializer,
            404: "Task Not Found",
            500: "Server Error",
        },
    )
    def get(self, request, *args, **kwargs):
        queryset = Task.objects.filter(assigned_by=request.user.id)
        if not queryset:
             return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = TaskSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
   
    @swagger_auto_schema(
        tags=["Institute  Task"],
        operation_description="Institute Task Create",
        request_body=InstituteTaskCreateSerializer,
        responses={
            201: InstituteTaskCreateSerializer,
            400: "Bad Request",
            500: "Server Error",
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = InstituteTaskCreateSerializer(data=request.data)
        # Here may be a teacher or 2 or more students in a batch or a batch of all students
        if serializer.is_valid():
            task_type = serializer.validated_data.get("task_type", None)
            task = Task.objects.create(
                title=serializer.validated_data.get("title", None),
                description=serializer.validated_data.get("description", None),
                assigned_by=request.user,
                user_type=Task.UserType.INSTITUTE,
                task_type=task_type,
                task_url=serializer.validated_data.get("task_url", None),
                due_date=serializer.validated_data.get("due_date", None),
            )
            assigned_to = serializer.validated_data.get("assigned_to", None)
            if task_type:
                if task_type == "individual":
                    #  If the Institute needs to send any task for each batches of 2 or more but not full of students
                    Q_filter = Q(id__in=assigned_to)

                elif task_type == "teacher":
                    # If the Institute needs to send task to teacher
                    Q_filter = Q(email=assigned_to[0])

                elif task_type == "batch":
                    # If the Institute needs to send task a batch of students
                    Q_filter = Q(student_profile__batch__id__in=assigned_to)

                # I need Id only so i optimized query using values_list
                users = User.objects.filter(Q_filter).values_list("id", flat=True)

                task.assigned_to.add(*users)  # unpacking from [1,2,3,4...] to 1, 2, 3
                task.save()
            return Response(TaskSerializer(task).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InstituteTaskUpdateAPIView(APIView):
    @swagger_auto_schema(
        tags=["Institute Task"],
        operation_description="Institute Task Fetch",
        responses={
            200: TaskSerializer,
            404: "Task Not Found",
            500: "Server Error",
        },
    )
    def get(self, request, pk=None, *args, **kwargs):
        instance = Task.objects.filter(id=pk).first()
        if not instance:
             return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = TaskSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=["Institute  Task"],
        operation_description="Institute Task Update",
        request_body=InstituteTaskCreateSerializer,
        responses={
            200: InstituteTaskCreateSerializer,
            404: "Task Not Found",
            500: "Server Error",
        },
    )
    def put(self, request, pk=None, *args, **kwargs):
        instance = Task.objects.filter(id=pk, assigned_by=request.user.id).first()
        if not instance:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = InstituteTaskCreateSerializer(data=request.data)
        if serializer.is_valid():
            assigned_to = serializer.validated_data.get("assigned_to")
            instance.title = serializer.validated_data.get("title", instance.title)
            instance.description = serializer.validated_data.get(
                "description", instance.description
            )
            instance.task_type = serializer.validated_data.get(
                "task_type", instance.task_type
            )
            instance.task_url = serializer.validated_data.get(
                "task_url", instance.task_url
            )
            instance.document = serializer.validated_data.get(
                "document", instance.document
            )
            instance.due_date = serializer.validated_data.get(
                "due_date", instance.due_date
            )
            Q_filter = Q()
            if instance.task_type == "individual":
                Q_filter = Q(id__in=assigned_to)
            elif instance.task_type == "teacher":
                instance.assigned_to.clear()
                Q_filter = Q(email=assigned_to[0])
            elif instance.task_type == "batch":
                Q_filter = Q(student_profile__batch__id__in=assigned_to)
            users = User.objects.filter(Q_filter).values_list("id", flat=True)
            instance.assigned_to.add(*users)
            instance.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["Institute Task"],
        operation_description="Institute Task Delete",
        responses={
            200: "Task Deleted Successfully",
            404: "TaskAssignment Not Found",
            500: "Server Error",
        },
    )
    def delete(self, request, pk=None, *args, **kwargs):
        instance = Task.objects.filter(id=pk).first()
        if instance:
            instance.delete()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)


class StudentTaskAssignmentUpdateAPIView(APIView):
    @swagger_auto_schema(
        tags=["Institute TaskAssignment"],
        operation_description="Institute Student TaskAssignment Fetch",
        responses={
            200: TaskAssignmentSerializer,
            404: "TaskAssignment Not Found",
            500: "Server Error",
        },
    )
    def get(self, request, task_id=None, pk=None, user_id=None, *args, **kwargs):
        task = Task.objects.filter(id=task_id).first()
        if not task:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if task.task_type == "teacher":
            user_details = TaskAssignment.objects.prefetch_related("user").filter(
                task_id=task_id
            )
        else:
            user_details = TaskAssignment.objects.prefetch_related(
                Prefetch(
                    "user",
                    queryset=User.objects.select_related(
                        "student_profile__batch"
                    ).annotate(batch_name=F("student_profile__batch__name")),
                ),
            ).filter(task_id=task.id)
        serializer = TaskAssignmentSerializer(user_details, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=["Institute TaskAssignment"],
        operation_description="Institute Student TaskAssignment Update",
        request_body=TaskAssignmentSerializer,
        responses={
            200: TaskAssignmentSerializer,
            400: "Bad Request",
            404: "TaskAssignment Not Found",
            500: "Server Error",
        },
    )
    def put(self, request, task_id=None, pk=None, user_id=None, *args, **kwargs):
        instance = TaskAssignment.objects.filter(
            id=pk, task=task_id, user=user_id
        ).first()
        if not instance:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = TaskAssignmentSerializer(instance)
        if serializer.is_valid():
            instance.is_completed = serializer.validated_data.get(
                "is_completed", instance.is_completed
            )
            instance.is_submitted = serializer.validated_data.get(
                "is_completed", instance.is_submitted
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
