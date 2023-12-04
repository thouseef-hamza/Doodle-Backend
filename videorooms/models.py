from django.db import models
from accounts.models import User

# Create your models here.
from institutes.models import AbstractDate


class ClassRoom(AbstractDate):
    class ClassRoomType(models.TextChoices):
        PRIVATE = "private", "Private"
        PUBLIC = "public", "Public"

    class ClassRoomStatus(models.TextChoices):
        IN_ACTIVE = "inactive", "In Active"
        ACTIVE = "active", "Active"

    hosted_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="hosted_by_classroom"
    )
    topic = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    password = models.CharField(max_length=30, null=True, blank=True)
    room_status = models.CharField(
        max_length=10,
        choices=ClassRoomStatus.choices,
        default=ClassRoomStatus.IN_ACTIVE,
    )
    room_code = models.CharField(max_length=15, blank=True, null=True)
    room_type = models.CharField(
        max_length=10, choices=ClassRoomType.choices, default=ClassRoomType.PRIVATE
    )

    def __str__(self) -> str:
        return self.hosted_by + " - " + self.topic


class Participant(models.Model):
    classroom = models.ForeignKey(
        ClassRoom, on_delete=models.CASCADE, related_name="classroom_participants"
    )
    participant = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_participant"
    )
    audio_turned = models.BooleanField(default=False)
    video_turned = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.classroom
