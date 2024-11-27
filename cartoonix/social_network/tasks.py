import logging
from celery import shared_task
from .models import Notification

logger = logging.getLogger('notifications')


@shared_task
def create_notification(recipient_id, actor_id, verb, target_content_type=None, target_object_id=None):
    """
    Asynchronously creates a notification.
    """
    notification = Notification.objects.create(
        recipient_id=recipient_id,
        actor_id=actor_id,
        verb=verb,
        target_content_type_id=target_content_type,
        target_object_id=target_object_id
    )
    logger.info(f"Notification {notification.id} created for user {recipient_id} by actor {actor_id}: '{verb}'.")

    return f"Notification created for user {recipient_id}"


@shared_task
def add(x, y):
    return x + y


@shared_task
def test_task():
    print("Test task executed")
    return "Test task completed"
