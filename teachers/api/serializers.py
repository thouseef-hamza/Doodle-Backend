from rest_framework import serializers
from ..models import TeacherProfile
from accounts.models import User


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherProfile
        fields = "__all__"


class TeacherProfileSerializer(serializers.ModelSerializer):
    profile = TeacherSerializer(source="teacher_profile")

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "username",
            "profile",
        )
