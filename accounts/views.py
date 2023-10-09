from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from .api.serializers import (
     TeacherRegisterationSerializer,
     InstituteRegisterationSerializer
)
from .models import User
from rest_framework.authentication import authenticate
from .service.messages import MessageHandler

import datetime,random
from datetime import timedelta
from django.conf import settings
message_otp=MessageHandler()

# Create your views here.
class TeacherRegisterationAPIView(APIView):
     
     def post(self,request,*args, **kwargs):
          serializer=TeacherRegisterationSerializer(data=request.data)
          if serializer.is_valid():
               otp=random.randint(1000,9999)
               otp_expiry=datetime.now()+timedelta(minutes=3)
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
               otp=random.randint(1000,9999)
               user=User.objects.create(
                    institute_name=serializer.validated_data['institute_name'],
                    email=serializer.validated_data['email'],
                    phone_number=serializer.validated_data['phone_number'],
                    otp=otp,
                    max_otp_try=settings.MAX_OTP_TRY,
                    is_active=False,
                    is_institute=True,
               )
               user.set_password(serializer.validated_data['password'])
               user.save()
               message_otp.send_otp_on_phone(user.phone_number,user.otp)
               response_data={
                    "msg":"Teacher Registered Successfully",
                    "data":{
                         "user_id":user.id,
                         "user":user.email,
                         "is_institute":user.is_institute,
                         "is_active":user.is_active,
                         "is_blocked":user.is_blocked
                    }
               }
               return Response(response_data,status=status.HTTP_201_CREATED)
          return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
     
     def patch(self,request,*args, **kwargs):
          otp=request.data["otp"]
          user_id=request.data["user_id"]   
          if otp and user_id:
               return message_otp.verify_otp(otp,pk=user_id) # Response Handled in MessageHandler() class
          
          return Response({"msg":"There is No OTP That you Entered"},status=status.HTTP_400_BAD_REQUEST)
          
               
               