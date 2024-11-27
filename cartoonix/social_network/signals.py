from django.dispatch import Signal, receiver
from .tasks import create_notification

friend_request_sent = Signal()
friend_request_accepted = Signal()
post_liked = Signal()
comment_added = Signal()

@receiver(friend_request_sent)
def handle_friend_request_sent(sender, from_user, to_user, **kwargs):
    create_notification.delay(
        recipient_id=to_user.id,
        actor_id=from_user.id,
        verb='sent you a friend request'
    )


@receiver(friend_request_accepted)
def handle_friend_request_accepted(sender, from_user, to_user, **kwargs):
    create_notification.delay(
        recipient_id=from_user.id,
        actor_id=to_user.id,
        verb='accepted your friend request'
    )


@receiver(post_liked)
def handle_post_liked(sender, post, user, **kwargs):
    create_notification.delay(
        recipient_id=post.author.id,
        actor_id=user.id,
        verb='liked your post',
        target_content_type=post._meta.model_name,
        target_object_id=post.id
    )


@receiver(comment_added)
def handle_comment_added(sender, post, user, comment, **kwargs):
    create_notification.delay(
        recipient_id=post.author.id,
        actor_id=user.id,
        verb='commented on your post',
        target_content_type=post._meta.model_name,
        target_object_id=post.id
    )
