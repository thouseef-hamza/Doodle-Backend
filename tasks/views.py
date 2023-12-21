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
from drf_yasg.utils import swagger_auto_schema
from silk.profiling.profiler import silk_profile
from rest_framework_simplejwt.authentication import JWTAuthentication
from institutes.pagination import LargeResultPagination

# Create your views here.


class InstituteTaskListCreateAPIView(APIView):
    authentication_classes = (JWTAuthentication,IsAuthenticated)

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
    @silk_profile(name="Institute Task List")
    def get(self, request, *args, **kwargs):
        # Each Institute Have Their Own Tasks,
        # So I filtered based on the institute this will makes only effifcient filtering
        instance = Task.objects.filter(assigned_by=request.user.id).values(
            "id", "title", "description", "task_type"
        )
        if not instance:
            return Response({}, status=status.HTTP_200_OK)
        paginator=LargeResultPagination()
        queryset=paginator.paginate_queryset(instance,request)
        response_data={
            "total_page":len(instance) // paginator.page_size,
            "tasks":queryset
        }
        return Response(response_data, status=status.HTTP_200_OK)

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
    @silk_profile(name="Institute Task List")
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
            if task_type and assigned_to:
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
        print(serializer.errors)
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
        # Each Institute Have Their Own Tasks,
        # So I filtered based on the institute this will makes only effifcient filtering
        instance = (
            Task.objects.filter(id=pk, assigned_by=request.user.id).first()
        )
        if not instance:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        serializer=TaskSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

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
        if not instance:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = InstituteTaskCreateSerializer(data=request.data)
        print(serializer)
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
            instance.assigned_to.clear()
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
    @silk_profile(name="Ins Task Update")
    def delete(self, request, pk=None, *args, **kwargs):
        instance = self.get_queryset(pk, request.user.id)
        # clear = request.GET.get("clear", None)
        # remove = request.GET.getlist("remove", None)
        # if clear or remove:
        #     if clear:
        #         task.assigned_to.clear()
        #         task.save()
        #         return Response(status=status.HTTP_205_RESET_CONTENT)
        #     # For Removing Specific users from junction table
        #     if remove:
        #         users = User.objects.filter(id__in=remove)
        #         task.assigned_to.remove(*users)
        #         task.save()
        #         return Response({"msg":"Specified User Removed Successfully"},status=status.HTTP_200_OK)
        if instance:
            instance.delete()
            return Response(
                {"msg": "Task Deleted Successfully"}, status=status.HTTP_204_NO_CONTENT
            )
        return Response({"msg": "Task Not Found"}, status=status.HTTP_404_NOT_FOUND)
        # For clearing all the users from junction table


class StudentTaskAssignmentListAPIView(APIView):
    # This view is for Institute
    def get(self, request, task_id=None, *args, **kwargs):
        search = request.GET.get("search", None)
        completed = request.GET.get("completed", None)
        submitted = request.GET.get("submitted", None)
        task_status = request.GET.get("status", None)
        Q_filter = Q(task_id=task_id)
        if completed or submitted or task_status or search:
            if completed:
                Q_filter &= Q(is_completed=True)
            elif submitted:
                Q_filter &= Q(is_submitted=True)
            elif task_status and task_status.lower() in [
                "good",
                "fair",
                "needs_improvement",
                "reviewing",
            ]:
                Q_filter &= Q(status=task_status.lower())
            elif search:
                Q_filter &= (
                    Q(user__first_name__icontains=search)
                    | Q(user__last_name__icontains=search)
                    | Q(user__unique_code__icontains=search)
                )
        # Fetch Details from 4 models (User (Unique Code Needed) <--- O to O ---> Student Profile (In this profile Have Batch Foriegn) <--- F to O ---> Batch (batch name needed))
        # Used F() for not making nested batch name
        queryset = TaskAssignment.objects.prefetch_related(
            Prefetch(
                "user",
                queryset=User.objects.select_related("student_profile__batch").annotate(
                    batch_name=F("student_profile__batch__name")
                ),
            ),
        ).filter(Q_filter)
        serializer = TaskAssignmentSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StudentTaskAssignmentGetUpdateAPIView(APIView):
    # User <-------> Task Assignment (Junction Table [Manual using through added additional fields status,submitting documents etc...]) <-------> Task (M 2 M relation)
    def get_student_queryset(self, _id):
        # Fetch Details from 4 models (User (Unique Code Needed) <--- O to O ---> Student Profile (In this profile Have Batch Foriegn) <--- F to O ---> Batch (batch name needed))
        # Used F() for not making nested batch name from student
        student = TaskAssignment.objects.prefetch_related(
            Prefetch(
                "user",
                queryset=User.objects.select_related("student_profile__batch").annotate(
                    batch_name=F("student_profile__batch__name")
                ),
            ),
        ).filter(pk=_id)
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
    def get(self, request, pk=None, *args, **kwargs):
        user_details = self.get_student_queryset(pk).first()
        serializer = TaskAssignmentSerializer(user_details)
        print(serializer.data)
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
        if not instance:
            return Response({"msg": "Task Not Found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = TaskAssignmentSerializer(data=request.data)
        if serializer.is_valid():
            instance.is_completed = serializer.validated_data.get(
                "is_completed", instance.is_completed
            )
            instance.is_submitted = serializer.validated_data.get(
                "is_submitted", instance.is_submitted
            )
            instance.status = serializer.validated_data.get("status", instance.status)
            instance.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
