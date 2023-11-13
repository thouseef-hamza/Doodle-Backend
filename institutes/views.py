from rest_framework.views import APIView

from .api.serializers import (
    InstituteSerializer,
    BatchSerializer,
    UserStudentSerializer,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import InstituteProfile
from accounts.models import User
from accounts.api.serializers import UserSerializer
from rest_framework.parsers import (
    MultiPartParser,
    FormParser,
    JSONParser,
    FileUploadParser,
)
from .models import Batch
from django.shortcuts import get_object_or_404
from students.models import StudentProfile
from django.db.models import Q
from accounts.helpers.password_generator import generate_random_password
from django.core.mail import EmailMessage
from django.conf import settings




class InstituteProfileGetUpdateAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get(self, request, *args, **kwargs):
        serializer = InstituteSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        serializer = InstituteSerializer(
            request.user, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

    def get(self, request, *args, **kwargs):
        queryset = Batch.objects.filter(institute__user_id=request.user.id).order_by(
            "id"
        )
        serializer = BatchSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

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

    def get(self, request, pk=None, *args, **kwargs):
        queryset = Batch.objects.filter(
            Q(id=pk) & Q(institute__user_id=request.user.id)
        ).first()
        serializer = BatchSerializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

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

    def get(self, request, *args, **kwargs):
        # Based on every each institute filtering their batches
        batches = Batch.objects.filter(institute__user_id=request.user.id)

        # According to filtered batches listing all the students
        students = User.objects.filter(student_profile__batch__id__in=batches).order_by(
            "id"
        )
        serializer = UserStudentSerializer(students, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        print("hello")
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

    def get(self, request, pk=None, *args, **kwargs):
        queryset = User.objects.filter(
            Q(id=pk) & Q(student_profile__batch__institute__user_id=request.user.id)
        ).first()
        serializer = UserStudentSerializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk=None,format=None, *args, **kwargs):
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
