from rest_framework.views import APIView

from .api.serializers import InstituteSerializer, InstituteProfileSerializer
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
                print(instances)
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
            user.institute_name = serializer.validated_data.get(
                "institute_name", user.institute_name
            )
            user.email = serializer.validated_data.get("email", user.email)
            user.phone_number = serializer.validated_data.get(
                "phone_number", user.phone_number
            )
            user.save(update_fields=["institute_name", "email", "phone_number"])

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
        # raw_sql = f"""
        # UPDATE institutes_instituteprofile
        # SET address='', city='',state='',postal_code='',website='',description='',establishment_year=''
        # WHERE user_id={request.user.id};
        # """
        # instance=InstituteProfile.objects.raw(raw_query=raw_sql)

        # return Response({"msg":"Institute Profile Cleared Successfully","users":InstituteProfileSerializer(instance).data},status=status.HTTP_205_RESET_CONTENT)
        # return Response({"msg":"User Not Found"},status=status.HTTP_404_NOT_FOUND)

        instance = InstituteProfile.objects.filter(user_id=request.user.id).first()
        if instance is not None:
            instance.delete()
            return Response(
                {"msg": "Institute Profile Deleted Successfully"},
                status=status.HTTP_205_RESET_CONTENT,
            )
        return Response({"msg": "User Not Found"}, status=status.HTTP_404_NOT_FOUND)
