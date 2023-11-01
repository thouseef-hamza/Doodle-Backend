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


class InstituteProfileAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get(self, request, *args, **kwargs):
        serializer = InstituteSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class InstituteProfileUpdateAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)
    parser_classes = (MultiPartParser, FormParser, JSONParser, FileUploadParser)

    def get(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        serializer = InstituteSerializer(
            context={"user": request.user}, data=request.data, partial=True
        )
        if serializer.is_valid():
            """Here I am updating profile_image and profile data seperately but in one api"""

            user = User.objects.filter(id=request.user.id).first()
            # Here i am updating my profile image only
            if "profile_image" in request.FILES:
                instances = InstituteProfile.objects.filter(user=user)
                for instance in instances:
                    instance.profile_image = request.FILES["profile_image"]
                instance.save(update_fields=["profile_image"])

                response_data = {
                    "msg": "Profile Image Updated Suceessfully",
                    "user": InstituteSerializer(user).data,
                }
                return Response(response_data, status=status.HTTP_200_OK)

            # Here i am updating Profile Data

            # Here  i updated User object
            institute_name = serializer.validated_data.get("institute_name")
            first_name, last_name = institute_name.split(" ", 1)
            user.first_name = first_name if first_name else user.first_name
            user.last_name = last_name if last_name else user.last_name
            user.email = serializer.validated_data.get("email", user.email)
            user.phone_number = serializer.validated_data.get(
                "phone_number", user.phone_number
            )
            user.save(
                update_fields=["first_name", "last_name", "email", "phone_number"]
            )

            # Here i updated user Profile Object
            InstituteProfile.objects.filter(user=user).update(
                **serializer.validated_data["profile"]
            )
            response_data = {
                "msg": "Profile Updated Suceessfully",
                "user": InstituteSerializer(user).data,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        instance = InstituteProfile.objects.filter(user_id=request.user.id).first()
        if instance is not None:
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
        if not queryset:
            return Response(
                {"msg": "No Batches Found"}, status=status.HTTP_404_NOT_FOUND
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
        if not queryset:
            return Response({"msg": "No Batch Found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = BatchSerializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk=None, *args, **kwargs):
        instance = Batch.objects.filter(
            Q(id=pk) & Q(institute__user_id=request.user.id)
        ).first()
        if instance is None:
            return Response({"msg": "No Data"}, status=status.HTTP_404_NOT_FOUND)
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
        if not students:
            return Response({"msg": "No Students"}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserStudentSerializer(students, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = UserStudentSerializer(data=request.data)
        if serializer.is_valid():
            batch_id = request.data.get("batch_id", None)
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
            student.save(update_fields=["batch"])
            # Sending Unique Code and Password for User Login
            email = EmailMessage(
                subject=f"Login Credentials from {student.batch.institute.user.get_full_name()}",
                body=f"""
                    <html>
                        <body>
                            <p>Hi <strong>{user.get_full_name()},</strong></p>
                            <p>Your Account Has Been Created By Your Institute</p>
                            <p>Here is your Login ID: <span contenteditable>{user.unique_code}</span> and Password: <span contenteditable>{password}</span></p>
                        </body>
                    </html>
                    """,
                from_email=settings.EMAIL_HOST_USER,
                to=[user.email],
            )
            email.content_subtype = "html"
            email.send()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudentGetUpdateAPIView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk=None, *args, **kwargs):
        queryset = User.objects.filter(
            Q(id=pk) & Q(student_profile__batch__institute__user_id=request.user.id)
        ).first()
        if not queryset:
            return Response(
                {"msg": "Student not found"}, status=status.HTTP_400_BAD_REQUEST
            )
        serializer = UserStudentSerializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk=None, *args, **kwargs):
        student = User.objects.filter(
            Q(id=pk) & Q(student_profile__batch__institute__user_id=request.user.id)
        ).first()
        if not student:
            return Response(
                {"msg": "No Student Found"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = UserStudentSerializer(
            instance=student, data=request.data, partial=True
        )
        if serializer.is_valid():
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
