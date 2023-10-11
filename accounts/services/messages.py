from django.conf import settings
from twilio.rest import Client
import random, datetime
from django.utils import timezone
from ..models import User
from rest_framework import status
from rest_framework.response import Response
from django.core.mail import EmailMessage
from rest_framework.exceptions import NotFound
from ..helpers.password_generator import generate_random_password

class MessageHandler:
    # AUTH_USER_MODEL Getting
    def get_object(self, pk):
        try:
            user = User.objects.get(id=pk)
        except User.MultipleObjectsReturned:
            user=User.objects.filter(id=pk).first()
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )
        return user

    # Sending OTP via Twilio
    def send_otp_on_phone(self, phone_number, otp):
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=f"Your OTP is {otp}",
            from_=settings.TWILIO_PHONE_NUMBER,
            to=str(phone_number),
        )

    # Verifying OTP with User Model otp attribute
    def verify_otp(self, otp, pk=None):
        instance = self.get_object(pk)
        if not instance.is_active:
            
            # If User is not active and OTP Present
            if instance.otp == str(otp):
                print("yhgbfvdcx")

                instance.is_active = True
                instance.max_otp_try = settings.MAX_OTP_TRY
                password = generate_random_password()
                
                # Generate Unique Code Base on User Role
                if instance.is_institute:
                    instance.unique_code="ADMIN %04d" % instance.id
                if instance.is_student:
                    instance.unique_code="STU %05d" % instance.id
                
                instance.set_password(password)
                instance.save(update_fields=["is_active", "max_otp_try","password","unique_code"])
                    
                # Sending Unique Code and Password for User Login
                email = EmailMessage(
                    subject="Hi User Thank You For Registering with Us",
                    body=f"Here is your Login ID: {instance.unique_code} and Password: {password}",
                    from_email=settings.EMAIL_HOST_USER,
                    to=[instance.email],
                )
                email.send()
                return instance

            # If User is not active and Maximum OTP Try Reached
            if int(instance.max_otp_try) < -1:
                return Response(
                    {"msg": "Max OTP Attempt Please Generate New OTP"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            instance.max_otp_try = int(instance.max_otp_try) - 1
            instance.save(update_fields=["max_otp_try"])

            # If the user trying to enter OTP
            return Response(
                {f"You Have Only {instance.max_otp_try} Try left"},
                status=status.HTTP_200_OK,
            )
        # If User Is Already Verified
        from rest_framework.exceptions import AuthenticationFailed
        raise AuthenticationFailed("User is already Verified")

    # Regenerating OTP, two cases if the OTP Didn't reached Or Maximum OTP Try Reached
    def regenerate_otp(self, pk=None):
        otp = random.randint(1000, 9999)
        instance = self.get_object(pk)
        instance.otp = otp
        instance.max_otp_try = settings.MAX_OTP_TRY
        instance.save(update_fields=["otp", "max_otp_try"])
        self.send_otp_on_phone(instance.phone_number, otp)
        return instance


message_otp = MessageHandler()
