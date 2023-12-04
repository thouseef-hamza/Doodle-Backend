from django.core.management.base import BaseCommand, CommandParser
from tasks.models import Task


class Command(BaseCommand):
    help = "Removing Task"

    def handle(self, *args, **kwargs):
        count = Task.objects.all().count()
        task = Task.objects.all()
        task.delete()
        self.stdout.write(
            self.style.ERROR(f"{count} Task object deleted Succesfully")
        )
