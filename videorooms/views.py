from rest_framework.views import APIView
from .models import ClassRoom
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import status
from .api.serializers import ClassRoomCreateUpdateSerializer
from django.db.models import Q
from django.contrib.auth.hashers import make_password
import secrets,json

# Create your views here.


class ClassRoomListCreateAPIView(APIView):
    def get(self, request, *args, **kwargs):
        search = request.GET.get("search", None)
        Q_object = Q(hosted_by=request.user)
        if search:
            Q_object &= Q(topic__iexact=search) | Q(description__icontains=search)
        instance = ClassRoom.objects.filter(Q_object).values()
        if not instance:
            return Response([], status=status.HTTP_200_OK)
        return Response(instance, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = ClassRoomCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            ClassRoom.objects.create(
                hosted_by=request.user,
                topic=serializer.validated_data.get("topic", None),
                description=serializer.validated_data.get("description", None),
                start_date=serializer.validated_data.get("start_date", None),
                password=serializer.validated_data.get("password", None),
                room_status=serializer.validated_data.get("room_status", None),
                room_type=serializer.validated_data.get("room_type", None),
                room_code=secrets.token_urlsafe(8)[:8],
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClassRoomRetrieveUpdateAPIView(APIView):
    def get_queryset(self, pk, user):
        return ClassRoom.objects.filter(id=pk, hosted_by=user)

    def get(self, request, pk=None, *args, **kwargs):
        instance = self.get_queryset(pk, request.user).values().first()
        if not instance:
            return Response(
                {"msg": "ClassRoom Not Found"}, status=status.HTTP_404_NOT_FOUND
            )
        return Response(instance, status=status.HTTP_200_OK)

    def put(self, request, pk=None, *args, **kwargs):
        instance = self.get_queryset(pk, request.user).first()
        if not instance:
            return Response(
                {"msg": "ClassRoom Not Found"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = ClassRoomCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            instance.topic = serializer.validated_data.get("topic", instance.topic)
            instance.description = serializer.validated_data.get(
                "description", instance.description
            )
            instance.start_date = serializer.validated_data.get(
                "start_date", instance.start_date
            )
            instance.password = serializer.validated_data.get(
                "password", instance.password
            )
            instance.room_status = serializer.validated_data.get(
                "room_status", instance.room_status
            )
            instance.room_type = serializer.validated_data.get(
                "room_type", instance.room_type
            )
            instance.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        instance = self.get_queryset(pk, request.user)
        if not instance:
            return Response(
                {"msg": "ClassRoom Not Found"}, status=status.HTTP_404_NOT_FOUND
            )
        instance.delete()
        return Response(
            {"msg": "Classroom Deleted Successfully"}, status=status.HTTP_204_NO_CONTENT
        )
        
class VideoRoomJoin(APIView):
    def post(self,request):
        room_code = json.loads(request.data.get("room_code",None))
        password = json.loads(request.data.get("password",None))
        classroom = ClassRoom.objects.filter(room_code=room_code).first()
        if not classroom:
            return Response({"msg":"There is no class room actively"},status=status.HTTP_404_NOT_FOUND)
        if classroom.password == password.strip():
            return JsonResponse({"user":request.user})
        return Response({"msg":"Invalid Room Code or Password"},status=status.HTTP_400_BAD_REQUEST)