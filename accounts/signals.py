from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from institutes.models import Institute,InstituteProfile
from students.models import Student
from teachers.models import Teacher,TeacherProfile

@receiver(post_save, sender=User)
def create_user_instance(sender, instance, created, **kwargs):
     if created:
          if instance.is_institute:
               institute=Institute.objects.create(user=instance)
               InstituteProfile.objects.create(user=institute)
          elif instance.is_student: 
               Student.objects.create(user=instance)
          elif instance.is_teacher:
               teacher=Teacher.objects.create(user=instance)
               TeacherProfile.objects.create(user=teacher)
                      
post_save.connect(create_user_instance, sender=User)
