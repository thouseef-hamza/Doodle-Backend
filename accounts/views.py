from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from .api.serializers import (
    TeacherRegisterationSerializer,
    InstituteRegisterationSerializer,
    OTPVerificationSerializer,
    UserLoginSerializer,
    UserSerializer,
    ChangePasswordSerializer,
)
from .models import User
from .services.messages import message_otp

from django.contrib.auth import authenticate
from .jwt.tokens import MyTokenObtainPairSerializer
from django.urls import reverse_lazy
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_yasg.utils import swagger_auto_schema
from django.utils import timezone


# Create your views here.
class TeacherRegisterationAPIView(APIView):
    @swagger_auto_schema(
        tags=["Authentication"],
        operation_description="Teacher Registeration",
        operation_summary="This endpoint is used for teacher registeration",
        request_body=TeacherRegisterationSerializer,
        responses={
            200: TeacherRegisterationSerializer,
            400: "Bad Request",
            500: "errors",
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = TeacherRegisterationSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.create(
                first_name=serializer.validated_data["first_name"],
                last_name=serializer.validated_data["last_name"],
                username=serializer.validated_data["username"],
                email=serializer.validated_data["email"],
                phone_number=serializer.validated_data["phone_number"],
                is_teacher=True,
                is_active=False,
            )
            user.set_password(serializer.validated_data["password"])
            user.save(update_fields=["password"])
            return Response(
                {
                    "msg": "Teacher Registered Successfully",
                    "data": UserSerializer(user).data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InstituteRegisterationAPIView(APIView):
    @swagger_auto_schema(
        tags=["Authentication"],
        operation_description="Institute Registeration",
        operation_summary="This endpoint is used for institute registeration",
        request_body=InstituteRegisterationSerializer,
        responses={
            200: InstituteRegisterationSerializer,
            400: "bad request",
            500: "errors",
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = InstituteRegisterationSerializer(data=request.data)
        if serializer.is_valid():
            verification_sid = message_otp.send_otp_on_phone(
                serializer.validated_data["phone_number"]
            )
            if verification_sid == "invalid":
                return Response(
                    {"msg": "Invalid Phone Number"}, status=status.HTTP_404_NOT_FOUND
                )
            elif verification_sid == "unavailable":
                return Response(
                    {"msg": "Our Service is not available.Please Try Again Later"},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )
            else:
                institute_name = serializer.validated_data.pop("institute_name")
                institute_name_split = institute_name.split(" ", 1)
                first_name, last_name = (
                    institute_name_split[0],
                    institute_name_split[1] if len(institute_name_split) > 1 else " ",
                )
                user = User.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    email=serializer.validated_data["email"],
                    phone_number=serializer.validated_data["phone_number"],
                    verification_sid=verification_sid,
                    is_active=False,
                    is_institute=True,
                )

                return Response(
                    {
                        "msg": "Institute Registered Successfully",
                        "data": UserSerializer(user).data,
                    },
                    status=status.HTTP_201_CREATED,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OTPVerificationAPIView(APIView):
    @swagger_auto_schema(
        request_body=OTPVerificationSerializer,
        responses={
            200: UserSerializer,
            400: "Bad Request",
            503: "Service Unavailable",
        },
        tags=["Authentication"],
        operation_summary="Verify OTP for User",
        operation_description="This endpoint is used for OTP verification.",
    )
    # For OTP Verification
    def post(self, request, pk=None, *args, **kwargs):
        user = User.objects.filter(id=pk).first()
        serializer = OTPVerificationSerializer(data=request.data)
        if serializer.is_valid():
            otp = serializer.validated_data["otp"]
            instance = message_otp.verify_otp(
                user.verification_sid, otp=otp, id=pk
            )  # message_otp() is from .services.messages
            return Response(
                {
                    "msg": "Successfully Verified the user",
                    "data": UserSerializer(instance).data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body=OTPVerificationSerializer,
        responses={
            200: UserSerializer,
            204: "No Content",
            400: "Bad Request",
            503: "Service Unavailable",
        },
        tags=["Authentication"],
        operation_summary="Regenerate OTP for User",
        operation_description="This endpoint is used for regenerating OTP.",
    )
    # For OTP Regenerating
    def patch(self, request, pk=None, *args, **kwargs):
        serializer = OTPVerificationSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data.get("phone_number", None)
            verification_sid = message_otp.regenerate_otp(
                pk=pk, phone_number=phone_number
            )  # message_otp() is from .services.messages

            # Handling Twilio Exceptions
            if verification_sid == "Invalid Phone Number":
                return Response(
                    {"msg": "Invalid Phone Number"}, status=status.HTTP_400_BAD_REQUEST
                )

            elif verification_sid == "Service Unavailable":
                return Response(
                    {"msg": "Our Service is not available.Please Try Again Later"},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )
            else:
                user = User.objects.filter(id=pk).first()
                user.verification_sid = verification_sid
                user.save(update_fields=["verification_sid"])
                return Response(
                    {
                        "msg": "OTP Regenerated Successfully",
                        "data": UserSerializer(user).data,
                    },
                    status=status.HTTP_200_OK,
                )

        return Response({"msg": "No User ID"}, status=status.HTTP_204_NO_CONTENT)


class UserLoginAPIVew(APIView):
    @swagger_auto_schema(
        request_body=UserLoginSerializer,
        responses={
            200: UserLoginSerializer,
            400: "Bad Request",
        },
        tags=["Authentication"],
        operation_summary="Login User",
        operation_description="This endpoint is used for Institute and Student Login.",
    )
    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get("email", None)
            unique_code = serializer.validated_data.get("unique_code", None)
            password = serializer.validated_data["password"]

            # Custom claims for jwt tokens and
            # manually creating jwt token using Refresh Token
            # also configured in settings.py
            custom_token_serializer = MyTokenObtainPairSerializer()

            """
               I have Created a CustomAuthBackend in auth_backends.py.
               For Handling Email Auth and Unique Code Auth
            """
            if email is not None:
                user = authenticate(request, email=email, password=password)
                if user is not None:
                    token = custom_token_serializer.get_token(user)
                    return Response(
                        {
                            "mes": "User Log in Successfully",
                            "jwt_token": {
                                "access": str(token.access_token),
                                "refresh": str(token),
                            },
                            "data": UserSerializer(user).data,
                        },
                        status=status.HTTP_200_OK,
                    )
                return Response(
                    {"msg": "User Not Found"}, status=status.HTTP_404_NOT_FOUND
                )

            if unique_code is not None:
                user = authenticate(request, unique_code=unique_code, password=password)
                if user is not None:
                    token = custom_token_serializer.get_token(user)
                    if user.last_login is None:
                        url = reverse_lazy("user-change-password")
                        return Response(
                            {
                                "message": "User needs to redirect to change password",
                                "redirect-api": url,
                                "jwt_token": {
                                    "access": str(token.access_token),
                                    "refresh": str(token),
                                },
                                "data": UserSerializer(user).data,
                            },
                            status=status.HTTP_200_OK,
                        )
                    return Response(
                        {
                            "mes": "User Log in Successfully",
                            "jwt_token": {
                                "access": str(token.access_token),
                                "refresh": str(token),
                            },
                            "data": UserSerializer(user).data,
                        },
                        status=status.HTTP_200_OK,
                    )
                raise AuthenticationFailed("There is no User")
            return Response(
                {"msg": "There is no valid Credentials"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForgetPasswordAPIView(APIView):
    def patch(self, request, *args, **kwargs):
        pass


class ChangePasswordAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def patch(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            # Here i am checking he entered last password correctly or not
            if not request.user.check_password(serializer.data.get("old_password")):
                return Response(
                    {"msg": "Old password is incorrect.Try Again"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            request.user.set_password(serializer.validated_data["new_password"])
            request.user.last_login = timezone.now()
            request.user.save(update_fields=["password", "last_login"])
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
