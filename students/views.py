from rest_framework.views import APIView
from .api.serializers import StudentSerializer
from rest_framework.response import Response
from rest_framework import status
from accounts.models import User


class StudentUpdateAPIView(APIView):
    def get(self, request, *args, **kwargs):
        user = User.objects.filter(id=request.user.id).first()
        if not user:
            return Response({"msg": "No Data Found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = StudentSerializer(user)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        user = User.objects.filter(id=request.user.id).first()
        serializer = StudentSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
