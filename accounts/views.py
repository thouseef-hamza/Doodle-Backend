from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import datetime,random
from datetime import timedelta

from .api.serializers import (
     TeacherRegisterationSerializer,
     InstituteRegisterationSerializer
)
from .models import User

# Create your views here.

class TeacherRegisterationAPIView(APIView):
     
     def post(self,request,*args, **kwargs):
          serializer=TeacherRegisterationSerializer(data=request.data)
          if serializer.is_valid():
               otp=random.randint(1000,9999)
               # otp_expiry=datetime.now()+timedelta(minutes=3)
               "first_name","last_name","username","email","phone_number","password","password2","is_teacher","is_blocked"
               user=User.objects.create(
                    first_name=serializer.validated_data["first_name"],
                    last_name=serializer.validated_data["last_name"],
                    username=serializer.validated_data["username"],
                    email=serializer.validated_data["email"],
                    phone_number=serializer.validated_data["phone_number"],
                    is_teacher=True
               )
               user.set_password(serializer.validated_data['password'])
               user.save()
               response_data={
                    "msg":"Teacher Registered Successfully",
                    "data":{
                         "user":user.email,
                         "is_teacher":user.is_teacher,
                         "is_active":user.is_active,
                         "is_blocked":user.is_blocked
                    }
               }
               return Response(response_data,status=status.HTTP_201_CREATED)
          return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
class InstituteRegisterationAPIView(APIView):
     def post(self,request,*args, **kwargs):
          serializer=InstituteRegisterationSerializer(data=request.data)
          if serializer.is_valid():
               user=User.objects.create(
                    
               )
               user.set_password(serializer.validated_data['password'])
               user.save()
               response_data={
                    "msg":"Teacher Registered Successfully",
                    "data":{
                         "user":user.email,
                         "is_institute":user.is_institute,
                         "is_active":user.is_active,
                         "is_blocked":user.is_blocked
                    }
               }
               return Response(response_data,status=status.HTTP_201_CREATED)
          return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
               
               
