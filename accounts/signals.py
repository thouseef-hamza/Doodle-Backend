from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from institutes.models import InstituteProfile
from students.models import StudentProfile
from teachers.models import TeacherProfile


@receiver(post_save, sender=User)
def create_user_profile_instance(sender, instance, created, **kwargs):
    if created:
        if instance.is_institute:
            InstituteProfile.objects.create(user=instance)
        elif instance.is_student:
            StudentProfile.objects.create(user=instance)
        elif instance.is_teacher:
            TeacherProfile.objects.create(user=instance)


post_save.connect(create_user_profile_instance, sender=User)

# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     instance.instituteprofile.save()
