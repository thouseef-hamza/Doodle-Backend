from rest_framework import serializers
from ..models import ClassRoom


class ClassRoomCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassRoom
        fields = (
            "topic",
            "description",
            "start_date",
            "password",
            "room_status",
            "room_type",
        )
        extra_kwargs = {
            "password": {"required": False},
        }

    def validate_topic(self, value):
        return value.strip().title()

    def validate_description(self, value):
        return value.strip()

    def validate_password(self, value):
        return value.strip()

    def validate_room_status(self, value):
        return value.strip().lower()

    def validate_room_type(self, value):
        return value.strip().lower()
