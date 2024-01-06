from rest_framework import serializers
from ..models import User



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ["password"]


class TeacherRegisterationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={"input_type": "password"}, write_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "username",
            "email",
            "phone_number",
            "password",
            "password2",
        ]
        extra_kwargs = {"phone_number": {"required": True}}


class InstituteRegisterationSerializer(serializers.ModelSerializer):
    institute_name = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "institute_name", "email", "phone_number"]


class OTPVerificationSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6, required=False)
    phone_number = serializers.CharField(max_length=15)


class UserLoginSerializer(serializers.Serializer):
    email = serializers.CharField(required=False)
    unique_code = serializers.CharField(required=False)
    password = serializers.CharField(style={"input_type": "password"})


class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)
    old_password = serializers.CharField(required=True)

class ForgetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField()
    password2 = serializers.CharField()
    
    def validate(self, attrs):
        password = attrs.get("password")
        password2 = attrs.get("password2")
        if password and password2 and password == password2:
            return attrs
        return serializers.ValidationError("Password and Confirm Password is not match")
    
class ResetPasswordSerializer(serializers.Serializer):
        email=serializers.EmailField()
        
        class Meta:
            fields = ("email",)
            
        def validate_email(self,value):
            if User.objects.filter(email=value).exists():
                return value
            raise serializers.ValidationError({"msg":"User with this email does not exist"})
        
                
    