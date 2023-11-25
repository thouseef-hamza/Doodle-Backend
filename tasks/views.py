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
        tags=["Institute Task"],
        operation_description="Institute Task List",
        operation_summary="Listing Tasks",
        responses={
            200: TaskSerializer,
            404: "Task Not Found",
            500: "Server Error",
        },
    )
    def get(self, request, *args, **kwargs):
        queryset = Task.objects.filter(assigned_by=request.user.id)
        if not queryset:
            return Response({"msg": "Task Not Found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = TaskSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=["Institute Task"],
        operation_description="Institute Task Create",
        operation_summary="Creating New Task",
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
    def get_queryset(self, pk, user):
        return Task.objects.filter(id=pk, assigned_by=user).first()

    @swagger_auto_schema(
        tags=["Institute Task"],
        operation_description="Institute Task Fetch",
        operation_summary="Fetching Specified Task",
        responses={
            200: TaskSerializer,
            404: "Task Not Found",
            500: "Server Error",
        },
    )
    def get(self, request, pk=None, *args, **kwargs):
        instance = (
            Task.objects.filter(id=pk, assigned_by=request.user.id).values().first()
        )
        if not instance:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(instance, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=["Institute Task"],
        operation_description="Institute Task Update",
        operation_summary="Updating Specified Task",
        request_body=InstituteTaskCreateSerializer,
        responses={
            200: InstituteTaskCreateSerializer,
            404: "Task Not Found",
            500: "Server Error",
        },
    )
    def put(self, request, pk=None, *args, **kwargs):
        instance = self.get_queryset(pk, request.user.id)
        print(instance)
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
                Q_filter = Q(
                    email=assigned_to[0]
                )  # I am assigning a task only for 1 teacher
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
        operation_summary="Deleting Specified Task",
        responses={
            200: "Task Deleted Successfully",
            404: "TaskAssignment Not Found",
            500: "Server Error",
        },
    )
    def delete(self, request, pk=None, *args, **kwargs):
        instance = self.get_queryset(pk, request.user.id)
        if instance:
            instance.delete()
            return Response(
                {"msg": "Task Deleted Successfully"}, status=status.HTTP_200_OK
            )
        return Response({"msg": "Task Not Found"}, status=status.HTTP_404_NOT_FOUND)


class StudentTaskAssignmentGetUpdateAPIView(APIView):
    def get_task_queryset(self, pk, user):
        return Task.objects.filter(id=pk, assigned_by=user).first()

    def get_student_queryset(self, task_id):
        # Fetch Details from 4 models
        student = TaskAssignment.objects.prefetch_related(
            Prefetch(
                "user",
                queryset=User.objects.select_related("student_profile__batch").annotate(
                    batch_name=F("student_profile__batch__name")
                ),
            ),
        ).filter(task_id=task_id)
        return student

    @swagger_auto_schema(
        tags=["Institute TaskAssignment"],
        operation_description="Institute  TaskAssignment Fetch",
        responses={
            200: TaskAssignmentSerializer,
            404: "TaskAssignment Not Found",
            500: "Server Error",
        },
    )
    def get(self, request, task_id=None, pk=None, *args, **kwargs):
        task = self.get_task_queryset(pk=task_id, user=request.user.id)
        completed = request.GET.get("completed", None)
        submitted = request.GET.get("submitted", None)
        if not task:
            return Response(
                {"msg": "Tasks not found"}, status=status.HTTP_404_NOT_FOUND
            )
        if completed or submitted:
            print("ok")
            if completed:
                 Q_filter = Q(is_completed=completed.title())
            if submitted:
                 Q_filter = Q(is_submitted=submitted.title())
            print(Q_filter)     
            queryset = self.get_student_queryset(task.id).filter(Q_filter)
            serializer = TaskAssignmentSerializer(queryset,many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        if task.task_type == "teacher":
            user_details = TaskAssignment.objects.prefetch_related("user").filter(
                task_id=task.id
            )
        else:
            user_details = self.get_student_queryset(task_id)
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
    def put(self, request, pk=None, *args, **kwargs):
        instance = TaskAssignment.objects.filter(
            id=pk, task__assigned_by=request.user.id
        ).first()
        print(instance)
        if not instance:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = TaskAssignmentSerializer(data=request.data)
        if serializer.is_valid():
            instance.is_completed = serializer.validated_data.get(
                "is_completed", instance.is_completed
            )
            instance.is_submitted = serializer.validated_data.get(
                "is_submitted", instance.is_submitted
            )
            instance.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["Institute TaskAssignment"],
        operation_description="Institute Student TaskAssignment Delete",
        responses={
            200: "Users Removed Successfully",
            205: "All Users Cleared",
            500: "Server Error",
        },
    )
    def delete(self, request, task_id=None, pk=None):
        clear = request.GET.get("clear", None)
        remove = request.GET.getlist("remove", None)
        print(remove)
        task = self.get_task_queryset(pk=task_id, user=request.user.id)
        if not task:
             return Response({"msg":"Task Not Found"},status=status.HTTP_404_NOT_FOUND)
        
        # For clearing all the users from junction table
        if clear:
            task.assigned_to.clear()
            task.save()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        # For Removing Specific users from junction table
        if remove:
            users = User.objects.filter(id__in=remove)
            task.assigned_to.remove(*users)
            task.save()
            return Response(status=status.HTTP_200_OK)
