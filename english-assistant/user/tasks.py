import logging

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_email_to_user(
    self, user_id, subject, message, html_message=None, from_email=None
):
    """
    Send an email to a specific user by user ID.

    Args:
        user_id (int): The ID of the user to send email to
        subject (str): Email subject
        message (str): Plain text message
        html_message (str, optional): HTML message content
        from_email (str, optional): From email address (defaults to EMAIL_HOST_USER)

    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        # Get the user
        user = User.objects.get(id=user_id)

        if not user.email:
            logger.warning(f"User {user_id} has no email address")
            return False

        # Set default from_email if not provided
        if not from_email:
            from_email = settings.EMAIL_HOST_USER

        # Send the email
        result = send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )

        logger.info(f"Email sent successfully to user {user_id} ({user.email})")
        return result == 1

    except User.DoesNotExist:
        logger.error(f"User with ID {user_id} does not exist")
        return False

    except Exception as exc:
        logger.error(f"Failed to send email to user {user_id}: {str(exc)}")
        # Retry the task with exponential backoff
        try:
            raise self.retry(exc=exc, countdown=60 * (2**self.request.retries))
        except self.MaxRetriesExceededError:
            logger.error(f"Max retries exceeded for sending email to user {user_id}")
            return False


@shared_task(bind=True, max_retries=3)
def send_template_email_to_user(
    self, user_id, subject, template_name, context=None, from_email=None
):
    """
    Send a template-based email to a specific user by user ID.

    Args:
        user_id (int): The ID of the user to send email to
        subject (str): Email subject
        template_name (str): Name of the template file (without .html extension)
        context (dict, optional): Context data for the template
        from_email (str, optional): From email address (defaults to EMAIL_HOST_USER)

    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        # Get the user
        user = User.objects.get(id=user_id)

        if not user.email:
            logger.warning(f"User {user_id} has no email address")
            return False

        # Prepare context
        if context is None:
            context = {}

        # Add user to context
        context["user"] = user

        # Render the email template
        html_message = render_to_string(f"emails/{template_name}.html", context)
        plain_message = strip_tags(html_message)

        # Set default from_email if not provided
        if not from_email:
            from_email = settings.EMAIL_HOST_USER

        # Send the email
        result = send_mail(
            subject=subject,
            message=plain_message,
            from_email=from_email,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )

        logger.info(
            f"Template email sent successfully to user {user_id} ({user.email})"
        )
        return result == 1

    except User.DoesNotExist:
        logger.error(f"User with ID {user_id} does not exist")
        return False

    except Exception as exc:
        logger.error(f"Failed to send template email to user {user_id}: {str(exc)}")
        # Retry the task with exponential backoff
        try:
            raise self.retry(exc=exc, countdown=60 * (2**self.request.retries))
        except self.MaxRetriesExceededError:
            logger.error(
                f"Max retries exceeded for sending template email to user {user_id}"
            )
            return False

