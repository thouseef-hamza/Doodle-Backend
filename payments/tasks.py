from celery import shared_task
from institutes.models import Batch
from django.db.models import Prefetch
from payments.models import StudentPayment
from smtplib import SMTPException
from students.models import StudentProfile
from django.conf import settings
from django.db.models import Q, F
from django.utils import timezone
from io import BytesIO
from reportlab.pdfgen import canvas
from django.core.mail import EmailMessage
from PIL import Image


def create_pdf_from_png(png_content):
    pdf_buffer = BytesIO()
    pdf_canvas = canvas.Canvas(pdf_buffer)
    image = Image.open(png_content)
    pdf_canvas.drawInlineImage(image, 0, 0, width=400, height=400)
    pdf_canvas.save()
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()


def get_queryset(Q_filter):
    return (
        Batch.objects.filter(Q_filter)
        .select_related("institute__user", "institute_payment_detail")
        .prefetch_related(
            Prefetch(
                "student_batch", queryset=StudentProfile.objects.select_related("user")
            )
        )
    )


@shared_task
def send_student_payment_fees_to_email():
    current_month = timezone.now().strftime("%m")
    current_day = timezone.now().strftime("%d")
    Q_filter = (
        Q(is_scheduled=True)
        & Q(scheduled_date__month=current_month)
        & Q(scheduled_date__day=current_day)
    )
    batch_obj = get_queryset(Q_filter)
    for batch in batch_obj:
        sender = batch.institute_payment_detail
        payment_number = batch.institute_payment_detail.payment_number
        upi_id = batch.institute_payment_detail.upi_id
        try:
            payment_qr = create_pdf_from_png(batch.institute_payment_detail.payment_qr)
        except Exception as e:
            payment_qr = None
        batch_fee = batch.batch_fees
        due_date = batch.due_date
        institute_name = (
            batch.institute.user.first_name + " " + batch.institute.user.last_name
        )
        for students in batch.student_batch.all():
            student_email = students.user.email
            student = StudentPayment.objects.create(
                student=students, sender=sender, fee_amount=batch_fee
            )
            try:
                subject = f"Monthly Fees From - {institute_name.title()}"
                message = f"""Dear {students.user.first_name + " "+ students.user.last_name},
            Your Montly Fees {batch_fee} should be paid.This is a reminder for you. 
            Payment should be done before {due_date}
            PAYMENT NUMBER :- {payment_number} 
            UPI ID :-  {upi_id}"""
                from_email = settings.EMAIL_HOST_USER
                recipient_list = [student_email]
                email = EmailMessage(subject, message, from_email, recipient_list)
                email.attach(
                    f"Monthly Rent {timezone.now().date}", payment_qr, "application/pdf"
                ) if payment_qr else None
                email.send(fail_silently=True)
            except SMTPException as e:
                student.is_notified = False
                student.save(update_fields=["is_notified"])


@shared_task
def send_student_fees_overdue_email():
    current_month = timezone.now().strftime("%m")
    current_day = timezone.now().strftime("%d")
    Q_filter = (
        Q(is_scheduled=True)
        & Q(due_date__month=current_month)
        & Q(due_date__day=current_day)
    )
    batch_obj = get_queryset(Q_filter)
    for batch in batch_obj:
        payment_number = batch.institute_payment_detail.payment_number
        upi_id = batch.institute_payment_detail.upi_id
        try:
            payment_qr = create_pdf_from_png(batch.institute_payment_detail.payment_qr)
        except Exception as e:
            payment_qr = None
        batch_fee = batch.batch_fees
        institute_name = (
            batch.institute.user.first_name + " " + batch.institute.user.last_name
        )
        for students in batch.student_batch.all():
            student_email = students.user.email
            student = StudentPayment.objects.filter(fee_status="pending")
            try:
                subject = f"Monthly Fees From - {institute_name.title()}"
                message = f"""Dear {students.user.first_name + " "+ students.user.last_name},
            Your Montly Fees {batch_fee} should be paid by today.This is the last date for fee payment.Ignore If You Have Already Done The Payment
            PAYMENT NUMBER :- {payment_number} 
            UPI ID :-  {upi_id}"""
                from_email = settings.EMAIL_HOST_USER
                recipient_list = [student_email]
                email = EmailMessage(subject, message, from_email, recipient_list)
                email.attach(
                    f"Monthly Rent {timezone.now().date}", payment_qr, "application/pdf"
                ) if payment_qr else None
                email.send(fail_silently=True)
            except SMTPException as e:
                student.is_notified = False
                student.save(update_fields=["is_notified"])


@shared_task
def student_fees_overdue_penalty():
    current_month = timezone.now().strftime("%m")
    current_day = timezone.now().strftime("%d")
    Q_filter = Q(is_scheduled=True) & \
        (
            Q(due_date__month=current_month)
            & Q(due_date__day__gt=current_day)
        )\
        &(Q(student_batch__student_payment_fees__fee_status="pending")
        | Q(student_batch__student_payment_fees__fee_status="overdue"))
    batch_obj = Batch.objects.filter(Q_filter).prefetch_related(
        Prefetch(
            "student_batch",
            queryset=StudentProfile.objects.prefetch_related("student_payment_fees"),
        )
    ).distinct()
    print(batch_obj)
    for batch in batch_obj:
        print(
            batch,
            "=============================================================================================",
        )
        fee_penalty = batch.fee_penalty
        print(
            fee_penalty,
            "======================================================================================",
        )
        if fee_penalty:
            for student in batch.student_batch.all():
                print(
                    student,
                    "===================================================================================",
                )
                student.student_payment_fees.update(
                    fee_amount=F("fee_amount") + fee_penalty, fee_status="overdue"
                )
