from institutes.api.serializers import UserStudentSerializer
from accounts.models import User


# I am inheriting UserStudentSerializer from institute.api.serializers
class StudentSerializer(UserStudentSerializer):
    class Meta(UserStudentSerializer.Meta):
        model = User
        fields = UserStudentSerializer.Meta.fields
        read_only_fields = ("unique_code",)

    def validate(self, data):
        # validation done from parent class - UserStudentSerializer
        data = super().validate(data)
        return data

    def update(self, instance, validated_data):
        # update will done from parent class - UserStudentSerializer
        return super().update(instance, validated_data)
