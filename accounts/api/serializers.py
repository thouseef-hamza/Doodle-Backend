from rest_framework import serializers
from ..models import User

class TeacherRegisterationSerializer(serializers.ModelSerializer):
     password2 = serializers.CharField(style={'input_type':'password'},write_only=True)
     class Meta:
          model=User
          field=["first_name","last_name","username","email","phone_number","password","password2"]
          
class InstituteRegisterationSerializer(serializers.ModelSerializer):
     class Meta:
          model=User
          fields=["institute_name","email","phone_number"]
          

class OTPVerificationSerializer(serializers.Serializer):
     otp=serializers.CharField(max_length=6)
     user_id=serializers.IntegerField()
     