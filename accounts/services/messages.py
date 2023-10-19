from django.conf import settings
from twilio.rest import Client
import random, datetime
from django.utils import timezone
from ..models import User
from rest_framework import status
from rest_framework.response import Response
from django.core.mail import EmailMessage
from ..helpers.password_generator import generate_random_password
from twilio.base.exceptions import TwilioRestException
from rest_framework.exceptions import AuthenticationFailed


class MessageHandler:
    # AUTH_USER_MODEL Getting
    def get_object(self, pk):
        print(pk,"edrtfyguhijihgfdrftgyhujiyfghbnj")
        try:
            user = User.objects.get(id=pk)
            print(user)
        except User.MultipleObjectsReturned:
            user = User.objects.filter(id=pk).first()
        except User.DoesNotExist:
            raise AuthenticationFailed(
                {"error": "User not found"}
            )
        return user

    # Sending OTP via Twilio
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    def send_otp_on_phone(self, phone_number):
        try:
            verification = self.client.verify \
                            .v2 \
                            .services(settings.TWILIO_SERVICE_SID) \
                            .verifications \
                            .create(to=phone_number, channel='sms')
            print("verification",verification)
            return verification.sid
        except ConnectionError as e:
            raise e

    # Verifying OTP with User Model otp attribute
    def verify_otp(self, verification_sid, otp,id):
        print(id,"fghujiojkihugyftdfyguhjiokjohiguyftderdtfyguhijhugytfrtderdtfygh")
        instance = self.get_object(id)
        print(instance,"drtfyguhjiokjihugyfctdcfghnjojihugyftdcfgvbhnjomknjbvycftdxrfgvbhjnknbugvycftdxr")
        print(instance.is_active,"None")
        if not instance.is_active:
            try:
                verification_check = self.client.verify \
                .v2 \
                .services(settings.TWILIO_SERVICE_SID) \
                .verification_checks \
                .create(verification_sid=verification_sid, code=otp)
                print(verification_check.status)

            except TwilioRestException as e:
                raise e
            
            # If User is not active and OTP Present
            if  verification_check.status == "approved":
                instance.is_active = True
                password = generate_random_password()
                print("password", password)

                # Generate Unique Code Base on User Role
                if instance.is_institute:
                    instance.unique_code = "ADMIN %04d" % instance.id
                if instance.is_student:
                    instance.unique_code = "STU %05d" % instance.id
                print(instance.unique_code)

                instance.set_password(password)
                instance.save(
                    update_fields=[
                        "is_active",
                        "password",
                        "unique_code",
                    ]
                )

                # Sending Unique Code and Password for User Login
                email = EmailMessage(
                    subject="Hi User Thank You For Registering with Us",
                    body=f"Here is your Login ID: {instance.unique_code} and Password: {password}",
                    from_email=settings.EMAIL_HOST_USER,
                    to=[instance.email],
                )
                email.send()
                return instance

            # If the user trying to enter OTP
            return Response(
                {f"Some thing went wrong with you credentials Please Try Again Later"},
                status=status.HTTP_200_OK,
            )
        # If User Is Already Verified

        raise AuthenticationFailed("User is already Verified")

    # Regenerating OTP, two cases if the OTP Didn't reached Or Maximum OTP Try Reached
    def regenerate_otp(self, pk=None,phone_number=None):
        instance = self.get_object(pk)
        instance.phone_number = phone_number
        instance.save(update_fields=["phone_number"]) 
        self.send_otp_on_phone(instance.phone_number)
        return instance


message_otp = MessageHandler()
