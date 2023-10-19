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
from django.conf import settings
from .jwt.tokens import MyTokenObtainPairSerializer
from django.urls import reverse_lazy
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
import random


# Create your views here.
class TeacherRegisterationAPIView(APIView):
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
            return Response({
                "msg": "Teacher Registered Successfully",
                "data": UserSerializer(user).data,
            }, 
            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InstituteRegisterationAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = InstituteRegisterationSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.create(
                institute_name=serializer.validated_data["institute_name"],
                email=serializer.validated_data["email"],
                phone_number=serializer.validated_data["phone_number"],
                max_otp_try=settings.MAX_OTP_TRY,
                is_active=False,
                is_institute=True,
            )
            verification_sid=message_otp.send_otp_on_phone(user.phone_number)
            print(verification_sid)
            request.session['verfication_sid'] = verification_sid
            request.session['phone_number'] = user.phone_number
            
            return Response({
                "msg": "Institute Registered Successfully",
                "data": UserSerializer(user).data,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OTPVerificationAPIView(APIView):
    # For OTP Verification
    def post(self, request,pk=None ,*args, **kwargs):
        # verification_sid = request.session.get("verification_sid")
        verification_sid = "VEa7f3f7dc27c1da854f54115931bf9a24"
        print(verification_sid)
        serializer = OTPVerificationSerializer(data=request.data)
        if serializer.is_valid():
            otp = serializer.validated_data["otp"]
            instance = message_otp.verify_otp(verification_sid,otp=otp,id=pk)  # message_otp() is from .services.messages
            return Response({
                "msg": "Successfully Verified the user",
                "data": UserSerializer(instance).data,
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # For OTP Regenerating
    def patch(self, request,pk=None ,*args, **kwargs):
        serializer=OTPVerificationSerializer(data=request.data)
        if serializer.is_valid():
            phone_number=serializer.validated_data.get("phone_number",None)
            instance = message_otp.regenerate_otp(pk=pk,phone_number=phone_number)  # message_otp() is from .services.messages
             
            return Response({
                "msg": "OTP Regenerated Successfully",
                "data": UserSerializer(instance).data,
            }, status=status.HTTP_200_OK)
        return Response({"msg": "No User ID"}, status=status.HTTP_204_NO_CONTENT)


class UserLoginAPIVew(APIView):
    def post(self, request, *args, **kwargs):
        print(request.data)
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
                    return Response({
                        "mes": "User Log in Successfully",
                        "jwt_token": {
                            "access": str(token.access_token),
                            "refresh": str(token),
                        },
                        "data": UserSerializer(user).data,
                    }, status=status.HTTP_200_OK)
                return Response(
                    {"msg": "User Not Found"}, status=status.HTTP_404_NOT_FOUND
                )

            if unique_code is not None:
                user = authenticate(request, unique_code=unique_code, password=password)
                if user is not None:
                    token = custom_token_serializer.get_token(user)
                    if user.last_login is None:
                        url = reverse_lazy("user-change-password")
                        print("hiihiii")
                        return Response({
                            "message": "User needs to redirect to change password",
                            "redirect-api": url,
                            "jwt_token": {
                                "access": str(token.access_token),
                                "refresh": str(token),
                            },
                            "data": UserSerializer(user).data,
                        }, status=status.HTTP_200_OK)
                    print("iughbhbhbjh")
                    return Response({
                        "mes": "User Log in Successfully",
                        "jwt_token": {
                            "access": str(token.access_token),
                            "refresh": str(token),
                        },
                        "data": UserSerializer(user).data,
                    }, status=status.HTTP_200_OK)
                raise AuthenticationFailed("There is no User")
            return Response(
                {"msg": "There is no valid Credentials"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
            from django.utils import timezone
            request.user.last_login = timezone.now()
            request.user.save(update_fields=["password","last_login"])
            return Response({
                "msg": "User Password Changed Successfully",
                "user": UserSerializer(request.user).data,
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
