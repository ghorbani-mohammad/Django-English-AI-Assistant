from .tasks import send_email_to_user, send_template_email_to_user, send_bulk_email


def send_welcome_email(user_id):
    """
    Send a welcome email to a new user.

    Args:
        user_id (int): The ID of the user to send welcome email to

    Returns:
        AsyncResult: Celery task result
    """
    return send_email_to_user.delay(
        user_id=user_id,
        subject="Welcome to English Assistant!",
        message="Welcome to our English learning platform! We're excited to help you improve your English skills.",
        html_message="""
        <h2>Welcome to English Assistant!</h2>
        <p>Welcome to our English learning platform!</p>
        <p>We're excited to help you improve your English skills.</p>
        <p>Get started by exploring our features and lessons.</p>
        <p>Happy learning!</p>
        """,
    )


def send_password_reset_email(user_id, reset_link):
    """
    Send a password reset email to a user.

    Args:
        user_id (int): The ID of the user
        reset_link (str): The password reset link

    Returns:
        AsyncResult: Celery task result
    """
    return send_template_email_to_user.delay(
        user_id=user_id,
        subject="Password Reset - English Assistant",
        template_name="password_reset",
        context={"reset_link": reset_link},
    )


def send_notification_email(user_id, notification_message):
    """
    Send a notification email to a user.

    Args:
        user_id (int): The ID of the user
        notification_message (str): The notification message

    Returns:
        AsyncResult: Celery task result
    """
    return send_email_to_user.delay(
        user_id=user_id,
        subject="Notification - English Assistant",
        message=notification_message,
    )


def send_bulk_announcement(user_ids, announcement_title, announcement_message):
    """
    Send an announcement email to multiple users.

    Args:
        user_ids (list): List of user IDs
        announcement_title (str): The announcement title
        announcement_message (str): The announcement message

    Returns:
        AsyncResult: Celery task result
    """
    return send_bulk_email.delay(
        user_ids=user_ids,
        subject=f"Announcement: {announcement_title}",
        message=announcement_message,
    )
