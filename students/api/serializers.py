from accounts.models import User
from ..models import StudentProfile
from rest_framework import serializers
from tasks.models import TaskAssignment
import re


class UserStudentProfileUpdateSerializer(serializers.ModelSerializer):
    batch_name = serializers.CharField(source="batch.name")

    class Meta:
        model = StudentProfile
        fields = (
            "batch_name",
            "gender",
            "date_of_birth",
            "profile_picture",
            "address",
            "city",
            "state",
            "postal_code",
        )
        read_only_fields = "batch_name"


class UserStudentUpdateSerializer(serializers.ModelSerializer):
    profile = UserStudentProfileUpdateSerializer(source="student_profile")

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "phone_number", "profile")
        read_only_fields = ("unique_code",)

    def validate_email(self, value):
        if User.objects.exclude(id=self.instance.id).filter(email=value).exists():
            raise serializers.ValidationError({"email": "This email is already used"})
        return value

    def validate_first_name(self, value):
        if re.search(r"\d", value):
            raise serializers.ValidationError(
                {"first_name": "Firstname should not contains digits"}
            )
        return value

    def validate_last_name(self, value):
        if re.search(r"\d", value):
            raise serializers.ValidationError(
                {"last_name": "Lastname should not contains digits"}
            )
        return value

    def validate_phone_number(self, value):
        if (
            User.objects.exclude(id=self.instance.id)
            .filter(phone_number=value)
            .exists()
        ):
            raise serializers.ValidationError(
                {"phone_number": "This Phonenumber already exists"}
            )
        return value


class UserStudentSerializer(serializers.ModelSerializer):
    profile = UserStudentProfileUpdateSerializer(source="student_profile")

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "phone_number", "profile")
        
class UserStudentTaskAssignmentAPIView(serializers.ModelSerializer):
    class Meta:
        model=TaskAssignment
        fields=("submitted_url","submitted_document","feedback")
        
