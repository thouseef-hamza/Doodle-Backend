from django.shortcuts import render
from rest_framework.views import APIView
from accounts.models import User
from rest_framework.response import Response
from rest_framework import status
from .api.serializers import TeacherProfileSerializer, TeacherProfileUpdateSerializer

# Create your views here.


class TeacherProfileUpdateAPIView(APIView):
    def get_queryset(self, user):
        return User.objects.filter(id=user.id).select_related("teacher_profile").first()

    def get(self, request, *args, **kwargs):
        instance = self.get_queryset(request.user)
        if instance:
            serializer = TeacherProfileSerializer(instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"msg": "Profile Not Found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, *args, **kwargs):
        instance = self.get_queryset(request.user)
        serializer = TeacherProfileUpdateSerializer(data=request.data)
        if serializer.is_valid():
            instance.first_name = serializer.validated_data
            pass

    def delete(self, request, *args, **kwargs):
        instance = self.get_queryset(request.user)
        if instance:
            instance.delete()
            return Response(
                {"msg": "User Deleted Successfully"}, status=status.HTTP_204_NO_CONTENT
            )
        return Response({"msg": "User Not Found"}, status=status.HTTP_404_NOT_FOUND)
