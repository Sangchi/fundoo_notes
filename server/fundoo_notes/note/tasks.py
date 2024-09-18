from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from loguru import logger
from .models import Notes



@shared_task
def send_reminder_email(note_name,email):
    """
        A Celery task to send a plain text reminder email to the user.

    """
    try:
        
        body=f"Reminder for Note: {note_name}"
        subject = f"Reminder"
        send_mail(
        subject=subject,
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )
    except Exception as e:
        logger.info("Note not found")