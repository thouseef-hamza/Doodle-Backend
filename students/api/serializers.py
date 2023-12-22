from accounts.models import User
from ..models import StudentProfile
from rest_framework import serializers
from tasks.models import TaskAssignment
import re
from tasks.models import Task
from payments.models import StudentPayment, UserPaymentDetail


class UserStudentProfileUpdateSerializer(serializers.ModelSerializer):
    batch_name = serializers.CharField(source="batch.name", read_only=True)
    date_of_birth=serializers.CharField()
    

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
    
    def validate_date_of_birth(self, value):
        return value.split("T")[0]


class UserStudentUpdateSerializer(serializers.ModelSerializer):
    profile = UserStudentProfileUpdateSerializer(source="student_profile")
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "unique_code",
            "profile",
        )
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
    
  

    def validate_profile(self, profile):
        serializer = UserStudentProfileUpdateSerializer(instance=self.instance.student_profile,data=profile)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.validated_data


class UserStudentSerializer(serializers.ModelSerializer):
    profile = UserStudentProfileUpdateSerializer(source="student_profile")

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "unique_code",
            "profile",
        )


class UserStudentTaskAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskAssignment
        fields = ("submitted_url", "submitted_document", "feedback")


class InstitutePaymentDetails(serializers.ModelSerializer):
    class Meta:
        model = UserPaymentDetail
        fields = ("payment_number", "payment_qr", "payment_bank", "upi_id")


class UserStudentPaymentUpdateSerializer(serializers.ModelSerializer):
    payment_details = InstitutePaymentDetails(source="sender", read_only=True)

    class Meta:
        model = StudentPayment
        fields = ("fee_paid", "payment_id", "payment_method")


class StudentTaskGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = (
            "title",
            "description",
            "assigned_by",
            "assigned_to",
            "task_url",
            "document",
            "due_date",
        )


class TaskAssignmentGetSerializer(serializers.ModelSerializer):
    task_details = StudentTaskGetSerializer(source="task", read_only=True)

    class Meta:
        model = TaskAssignment
        fields = (
            "submitted_url",
            "submitted_document",
            "status",
            "feedback",
            "is_completed",
            "is_submitted",
        )

class ClassmatesGetSerializer(serializers.ModelSerializer):
    profile_picture=serializers.URLField(source="student_profile.profile_picture")
    class Meta:
        model=User
        fields=("first_name","last_name","email","phone_number","unique_code","profile_picture")