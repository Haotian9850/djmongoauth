from django.core.mail import send_mail
from .Email import Email

def send_email(email:Email):
    send_mail(
        subject=email.subject,
        message=email.text_message,
        from_email=email.from_email,
        recipient_list=[email.to_email],
        html_message=email.html_message
    )
