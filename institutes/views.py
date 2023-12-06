from rest_framework.views import APIView

from .api.serializers import (
    InstituteSerializer,
    BatchSerializer,
    UserStudentSerializer,
    JobCreateUpdateSerializer,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import InstituteProfile, Job
from accounts.models import User
from .models import Batch
from django.shortcuts import get_object_or_404
from students.models import StudentProfile
from django.db.models import Q
from accounts.helpers.password_generator import generate_random_password
from django.core.mail import EmailMessage
from drf_yasg.utils import swagger_auto_schema
from accounts.models import User
from django.db.models import F, Count
from datetime import date


class InstituteProfileGetUpdateAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    @swagger_auto_schema(
        tags=["Institute Profile"],
        operation_description="Institute Profile",
        responses={
            200: InstituteSerializer,
            400: "Bad Request",
            500: "Server Error",
        },
    )
    def get(self, request, *args, **kwargs):
        serializer = InstituteSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=["Institute Profile"],
        operation_description="Institute Profile Updation",
        request_body=InstituteSerializer,
        responses={
            200: InstituteSerializer,
            400: "Bad Request",
            500: "Server Error",
        },
    )
    def put(self, request, *args, **kwargs):
        serializer = InstituteSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["Institute Profile"],
        operation_description="Institute Profile",
        responses={
            200: InstituteSerializer,
            400: "Bad Request",
            500: "Server Error",
        },
    )
    def delete(self, request, *args, **kwargs):
        instance = User.objects.filter(id=request.user.id).first()
        if instance:
            instance.delete()
            return Response(
                {"msg": "Institute Profile Deleted Successfully"},
                status=status.HTTP_205_RESET_CONTENT,
            )
        return Response({"msg": "User Not Found"}, status=status.HTTP_404_NOT_FOUND)


class BatchListCreateAPIView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        tags=["Institute Batch"],
        operation_description="Institute Batch Fetch",
        responses={
            200: BatchSerializer,
            400: "Bad Request",
            500: "Server Error",
        },
    )
    def get(self, request, *args, **kwargs):
        # In this request user is institute
        # Based on institute i am filter their batches only
        # or else other institute can see other institute batches
        search = request.GET.get("search", None)
        Q_filter = Q(institute__user_id=request.user.id)
        if search:
            Q_filter &= Q(name__icontains=search)
        queryset = Batch.objects.filter(Q_filter).order_by("id")
        serializer = BatchSerializer(queryset, many=True)
        print(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=["Institute Batch"],
        operation_description="Institute Batch Creation",
        request_body=BatchSerializer,
        responses={
            200: BatchSerializer,
            400: "Bad Request",
            500: "Server Error",
        },
    )
    def post(self, request, *args, **kwargs):
        institute = get_object_or_404(InstituteProfile, user=request.user)
        serializer = BatchSerializer(data=request.data)
        if serializer.is_valid():
            batch = Batch.objects.create(
                institute=institute,
                name=serializer.validated_data.get("name", None),
                start_date=serializer.validated_data.get("start_date", None),
                description=serializer.validated_data.get("description", None),
            )
            return Response(BatchSerializer(batch).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BatchGetUpdateAPIView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        tags=["Institute Batch"],
        operation_description="Institute Batch Detail Fetch",
        responses={
            200: BatchSerializer,
            400: "Bad Request",
            500: "Server Error",
        },
    )
    def get(self, request, pk=None, *args, **kwargs):
        queryset = Batch.objects.filter(
            Q(id=pk) & Q(institute__user_id=request.user.id)
        ).first()
        serializer = BatchSerializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=["Institute Batch"],
        operation_description="Institute Batch Detail Update",
        request_body=BatchSerializer,
        responses={
            200: BatchSerializer,
            400: "Bad Request",
            500: "Server Error",
        },
    )
    def put(self, request, pk=None, *args, **kwargs):
        instance = Batch.objects.filter(
            Q(id=pk) & Q(institute__user_id=request.user.id)
        ).first()
        serializer = BatchSerializer(instance, data=request.data)
        if serializer.is_valid():
            instance.name = serializer.validated_data.get("name", instance.name)
            instance.description = serializer.validated_data.get(
                "description", instance.description
            )
            instance.save(update_fields=["name", "description"])
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["Institute Batch"],
        operation_description="Institute Batch Detail Update",
        responses={
            204: "No Content",
            404: "Not Found",
            500: "Server Error",
        },
    )
    def delete(self, request, pk=None, *args, **kwargs):
        batch = Batch.objects.filter(
            Q(id=pk) & Q(institute__user_id=request.user.id)
        ).first()
        if not batch:
            return Response({"msg": "No Batch Found"}, status=status.HTTP_404_NOT_FOUND)
        batch.delete()
        return Response(
            {"msg": "Batch Deleted Successfully"}, status=status.HTTP_204_NO_CONTENT
        )


class StudentListCreateAPIView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        tags=["Institute Student"],
        operation_description="Institute Student Fetch",
        responses={
            200: UserStudentSerializer,
            404: "Not Found",
            500: "Server Error",
        },
    )
    def get(self, request, *args, **kwargs):
        # Based on every each institute filtering their batches
        batches = Batch.objects.filter(institute__user_id=request.user.id)
        search = request.GET.get("search", None)
        print(search)
        Q_filter = Q(student_profile__batch__id__in=batches)
        if search:
            Q_filter &= (
                Q(first_name__iexact=search)
                | Q(last_name__iexact=search)
                | Q(unique_code__iexact=search)
                | Q(email__iexact=search)
            )
        print(Q_filter)
        # According to filtered batches listing all the students
        students = User.objects.filter(Q_filter).order_by("id")
        serializer = UserStudentSerializer(students, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=["Institute Student"],
        operation_description="Institute Student Create",
        responses={
            201: UserStudentSerializer,
            400: "Not Found",
            500: "Server Error",
        },
    )
    def post(self, request, *args, **kwargs):
        batch_id = request.data.pop("batch_id", None)
        serializer = UserStudentSerializer(data=request.data)
        if serializer.is_valid():
            if batch_id is None:
                return Response(
                    {"msg": "Before Creating Students,You want to create Batch First"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            batch = get_object_or_404(Batch, id=int(batch_id))
            user = User.objects.create(
                first_name=serializer.validated_data.get("first_name", None),
                last_name=serializer.validated_data.get("last_name", None),
                email=serializer.validated_data.get("email", None),
                phone_number=serializer.validated_data.get("phone_number", None),
                is_student=True,
            )
            password = generate_random_password()
            user.unique_code = "STU %06d" % user.id
            user.set_password(password)
            user.save(update_fields=["unique_code", "password"])
            student = StudentProfile.objects.filter(user=user).first()
            student.batch = batch
            student.save()
            return Response(
                UserStudentSerializer(student.user).data, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudentGetUpdateAPIView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        tags=["Institute Student"],
        operation_description="Institute Student Fetch",
        responses={
            200: UserStudentSerializer,
            400: "Not Found",
            500: "Server Error",
        },
    )
    def get(self, request, pk=None, *args, **kwargs):
        queryset = User.objects.filter(
            Q(id=pk) & Q(student_profile__batch__institute__user_id=request.user.id)
        ).first()
        serializer = UserStudentSerializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=["Institute Student"],
        operation_description="Institute Student Update",
        request_body=UserStudentSerializer,
        responses={
            200: UserStudentSerializer,
            400: "Bad Request",
            500: "Server Error",
        },
    )
    def put(self, request, pk=None, format=None, *args, **kwargs):
        student = User.objects.filter(
            Q(id=pk) & Q(student_profile__batch__institute__user_id=request.user.id)
        ).first()
        serializer = UserStudentSerializer(
            instance=student, data=request.data, partial=True
        )
        if serializer.is_valid():
            batch_id = request.data.get("batch_id", None)
            student = User.objects.filter(id=pk).first()
            if batch_id is not None and student is not None:
                batch = Batch.objects.filter(id=int(batch_id)).first()
                student.student_profile.batch = batch
                student.student_profile.save()
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["Institute Student"],
        operation_description="Institute Student Delete",
        request_body=UserStudentSerializer,
        responses={
            204: "Student Deleted",
            404: "Student Not Found",
            500: "Server Error",
        },
    )
    def delete(self, request, pk=None, *args, **kwargs):
        student = User.objects.filter(
            Q(id=pk) & Q(student_profile__batch__institute__user_id=request.user.id)
        ).first()
        if not student:
            return Response(
                {"msg": "No Student Found"}, status=status.HTTP_404_NOT_FOUND
            )
        student.delete()
        return Response(
            {"msg": "User Deleted Successfully"}, status=status.HTTP_204_NO_CONTENT
        )


class JobListCreateAPIView(APIView):
    def get_queryset(self, user):
        return Job.objects.filter(company=user.id).values()

    @swagger_auto_schema(
        tags=["Institute Job"],
        operation_description="Institute Job List",
        responses={
            200: "Job List",
            500: "Server Error",
        },
    )
    def get(self, request, *args, **kwargs):
        instance = self.get_queryset(user=request.user)
        if instance:
            return Response(instance, status=status.HTTP_200_OK)
        return Response({}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=["Institute Job"],
        operation_description="Institute Job Create",
        request_body=JobCreateUpdateSerializer,
        responses={
            201: JobCreateUpdateSerializer,
            400: JobCreateUpdateSerializer,
            500: "Server Error",
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = JobCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            Job.objects.create(
                title=serializer.validated_data.get("title", None),
                description=serializer.validated_data.get("description", None),
                category=serializer.validated_data.get("category", None),
                job_type=serializer.validated_data.get("job_type", None),
                company=serializer.validated_data.get("company", None),
                salary=serializer.validated_data.get("salary", None),
            )
            return Response(
                {"msg": "Job Created Successfully"}, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class JobRetriveUpdateAPIView(APIView):
    def get_queryset(self, pk, user):
        return Job.objects.filter(id=pk, company=user.id)

    @swagger_auto_schema(
        tags=["Institute Job"],
        operation_description="Institute Job Retrieve",
        responses={
            200: "Job Rerieve",
            404: "Job Not Found",
            500: "Server Error",
        },
    )
    def get(self, request, pk=None, *args, **kwargs):
        instance = self.get_queryset(pk=pk, user=request.user).values().first()
        if instance:
            return Response(instance, status=status.HTTP_200_OK)
        return Response({"msg": "Job Not Found"}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        tags=["Institute Job"],
        operation_description="Institute Job Update",
        request_body=JobCreateUpdateSerializer,
        responses={
            200: JobCreateUpdateSerializer,
            404: "Job Not Found",
            500: "Server Error",
        },
    )
    def put(self, request, pk=None, *args, **kwargs):
        instance = self.get_queryset(pk=pk, user=request.user).first()
        if instance:
            serializer = JobCreateUpdateSerializer(data=request.data)
            if serializer.is_valid():
                instance.title = serializer.validated_data.get("title", instance.title)
                instance.description = serializer.validated_data.get(
                    "description", instance.description
                )
                instance.category = serializer.validated_data.get(
                    "category", instance.category
                )
                instance.job_type = serializer.validated_data.get(
                    "job_type", instance.job_type
                )
                instance.salary = serializer.validated_data.get(
                    "salary", instance.salary
                )
                instance.save(
                    update_fields=[
                        "title",
                        "description",
                        "category",
                        "job_type",
                        "salary",
                    ]
                )
                return Response(
                    {"msg": "Job Updated Successfully"}, status=status.HTTP_200_OK
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"msg": "Job Not Found"}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        tags=["Institute Job"],
        operation_description="Institute Job Delete",
        request_body=JobCreateUpdateSerializer,
        responses={
            200: "Job Deleted Successfully",
            404: "Job Not Found",
            500: "Server Error",
        },
    )
    def delete(self, request, pk=None, *args, **kwargs):
        instance = self.get_queryset(pk=pk, user=request.user).first()
        if instance:
            instance.delete()
            return Response(
                {"msg": "Job Deleted Successfully"}, status=status.HTTP_200_OK
            )
        return Response({"msg": "Job Not Found"}, status=status.HTTP_404_NOT_FOUND)


class InstituteDashboardAPIView(APIView):
    def get(self, request, *args, **kwargs):
        instance = Batch.objects.filter(institute=request.user.id).aggregate(
            batch_count=Count("id"), student_count=Count("student_batch")
        )

        print(instance)
        return Response(instance, status=status.HTTP_200_OK)


class TeacherListAPIView(APIView):
    def get(self, request, *args, **kwargs):
        instance = User.objects.filter(is_teacher=True).select_related(
            "teacher_profile"
        )
