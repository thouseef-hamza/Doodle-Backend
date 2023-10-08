from rest_framework import serializers
from ..models import User

# class UserRegisterationSerializer(serializers.ModelSerializer):
#      password2 = serializers.CharField(style={'input_type':'password'},write_only=True)
#      class Meta:
#           model = User
#           fields = '__all__'

class TeacherRegisterationSerializer(serializers.ModelSerializer):
     password2 = serializers.CharField(style={'input_type':'password'},write_only=True)
     class Meta:
          model=User
          field=["first_name","last_name","username","email","phone_number","password","password2"]
          
# class StudentRegisterationSerializer(serializers.ModelSerializer):
     
#      class Meta:
#           model=User
#           field=["first_name","last_name","email","phone_number","unique_code","password","is_student","is_blocked"]
          
class InstituteRegisterationSerializer(serializers.ModelSerializer):
     class Meta:
          model=User
          field=["institute_name","email","phone_number","unique_code","is_institute","is_blocked"]