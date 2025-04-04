from django.conf import settings
from django.core.mail import send_mail


class NotificationService:
    @staticmethod
    def send_email(to, subject, message):
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [to],
            fail_silently=False,
        )
