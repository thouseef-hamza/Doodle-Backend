from rest_framework import serializers
from ..models import InstituteProfile
from accounts.models import User


class InstituteProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstituteProfile
        fields = "__all__"
        extra_kwargs = {"user": {"read_only": True}}


class InstituteSerializer(serializers.ModelSerializer):
    profile = InstituteProfileSerializer()
    email = serializers.EmailField(required=True)
    phone_number = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = [
            "id",
            "institute_name",
            "email",
            "phone_number",
            "unique_code",
            "profile",
        ]
        extra_kwargs = {"unique_code": {"read_only": True}}

    def validate_email(self, value):
        user = self.context["user"]
        if User.objects.exclude(pk=user.id).filter(email=value).exists():
            raise serializers.ValidationError(
                {"email": "This email is already in use."}
            )
        return value

    def validate_phone_number(self, value):
        user = self.context["user"]
        if User.objects.exclude(pk=user.id).filter(phone_number=value).exists():
            raise serializers.ValidationError(
                {"email": "This Phone Number is already in use."}
            )
        return value

    def create(self, validated_data):
        profile_data = validated_data.pop("profile")
        user = User.objects.create(**validated_data)
        InstituteProfile.objects.create(user=user, **profile_data)
        return user
