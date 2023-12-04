from typing import Any
from django.core.management.base import BaseCommand, CommandParser
from faker import Faker
from tasks.models import Task
from accounts.models import User


fake = Faker()


class Command(BaseCommand):
    help = "Generating Task"

    def add_arguments(self, parser: CommandParser):
        parser.add_argument(
            "count", type=int, help="No of Tasks Needed to be Generated"
        )
        parser.add_argument(
            "-tt",
            "--tasktype",
            type=str,
            help="Define which task type individual/teacher/batch",
        )
        parser.add_argument(
            "-ut",
            "--usertype",
            type=str,
            help="Define which user type that assign task teacher/institute/",
        )
        parser.add_argument(
            "-e", "--email", type=str, help="For Setting Who Created this Task"
        )

    def handle(self, *args, **kwargs):
        count = kwargs["count"]
        tasktype = kwargs["tasktype"]
        usertype = kwargs["usertype"]
        email = kwargs["email"]
        if email:
            email = email
        else:
            email = "fsa@gmail.com"
        assigned_by,_ = User.objects.get_or_create(email=email)
        for i in range(count):
            if usertype:
                user_type = usertype
            else:
                user_type = "institute"
            if tasktype:
                task_type = f"{tasktype}"
            else:
                task_type = "individual"
            task = Task.objects.create(
                title=f"Task No 00{i}",
                description=fake.text(),
                assigned_by=assigned_by,
                task_type=task_type,
                user_type=user_type,
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Task {task.title} assigned_by= {task.assigned_by} Created successfully!"
                )
            )
