from django.conf import settings
from twilio.rest import Client
import random,datetime
from django.utils import timezone
from ..models import User
from rest_framework import status
from rest_framework.response import Response

class MessageHandler:
     
     # AUTH_USER_MODEL Getting 
     def get_object(self,pk):
          try:
               user=User.objects.get(id=pk)
               print("get_object() user",user)
          except User.DoesNotExist:
               raise 
          return user
     
     # Sending OTP via Twilio
     def send_otp_on_phone(self,phone_number,otp):
          client=Client(settings.TWILIO_ACCOUNT_SID,settings.TWILIO_AUTH_TOKEN)
          message=client.messages.create(
               body=f"Your OTP is {otp}",
               from_=settings.TWILIO_PHONE_NUMBER,
               to=str(phone_number)
          )
     
     # Verifying OTP with User Model otp attribute
     def verify_otp(self,otp,pk=None):
          instance=self.get_object(pk)
          if not instance.is_active:
               
               # If User is not active and OTP Present
               if instance.otp == str(otp):
                    instance.is_active=True
                    instance.max_otp_try=settings.MAX_OTP_TRY
                    instance.save()
                    return Response({"msg":
                    "Successfully Verified the user."}, status=status.HTTP_200_OK
                    )
               instance.max_otp_try =  int(instance.max_otp_try)-1
               instance.save()
               
               # If User is not active and Maximum OTP Try Reached
               if int(instance.max_otp_try) == -1:
                    return Response({"msg":"Max OTP Attempt Please Generate New OTP"},status=status.HTTP_400_BAD_REQUEST)
               
               # If the user trying to enter OTP
               return Response({f"You Have Only {instance.max_otp_try} Try left"},status=status.HTTP_200_OK)   
          
          # If User Is Already Verified
          return Response(
          "User is Already Verified",
          status=status.HTTP_400_BAD_REQUEST,
          )
          
     
     # Regenerating OTP, two cases if the OTP Didn't reached Or Maximum OTP Try Reached
     def regenerate_otp(self,pk=None):
          otp=random.randint(1000,9999)
          instance=self.get_object(pk)
          instance.otp=otp
          instance.max_otp_try=settings.MAX_OTP_TRY
          instance.save()
          self.send_otp_on_phone(instance.phone_number,otp)
          return Response({"msg":"Regenerate OTP Successfullly"},status=status.HTTP_200_OK)
          