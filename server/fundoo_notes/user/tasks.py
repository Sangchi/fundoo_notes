from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils.html import format_html
from django.core.mail import BadHeaderError


@shared_task(bind=True)
def send_verification_email(self,user_email, link):
    """
    A Celery task to send a verification email to the user.
    
    Args:
        user_email (str): The email address of the user.
        link (str): The verification link.

    Returns:
        None
    """
    subject = 'Please verify your email address'
    plain_message = f'Hi,\n\nPlease verify your email by clicking on the link below:\n{link}\n\nThank you!'
    html_message = format_html(
        '<p>Hi,</p>'
        '<p>Please verify your email by clicking on the link below:</p>'
        '<p><a href="{}">Verify Email</a></p>'
        '<p>Thank you!</p>',
        link
    )

    try:
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            fail_silently=False,
            html_message=html_message
        )
    except BadHeaderError:
        # Handle bad header errors specifically
        print(f"Bad header error while sending email to {user_email}")