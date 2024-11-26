import logging
from django.contrib.auth.models import User, AbstractUser
from django.db import models
from PIL import Image
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from ai.models import VideoPrompt
from django import forms
from django.dispatch import receiver


logger = logging.getLogger('model_logger')  # Логгер для моделей

class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default_post.jpg', upload_to='post_pics')
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)

    def __str__(self):
        return self.title

    def total_likes(self):
        return self.likes.count()


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'image']


class Comment(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')

    def __str__(self):
        return f"Comment by {self.author} on {self.post}"


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    friends = models.ManyToManyField('self', symmetrical=False, related_name='user_friends', blank=True)
    image = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        logger.info(f"Profile for user {self.user.username} is being saved.")
        super().save(*args, **kwargs)

    def add_friend(self, profile):
        self.friends.add(profile)
        self.save()
        logger.info(f"User {self.user.username} added {profile.user.username} as a friend.")

    def remove_friend(self, profile):
        self.friends.remove(profile)
        self.save()
        logger.info(f"User {self.user.username} removed {profile.user.username} from friends.")

    def is_friend(self, profile):
        is_friend = profile in self.friends.all()
        logger.debug(f"Checked friendship status between {self.user.username} and {profile.user.username}: {is_friend}.")
        return is_friend


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image', 'bio']


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        logger.info(f"Profile created for user {instance.username}.")


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
    logger.info(f"Profile saved for user {instance.username}.")


class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='friend_requests_sent', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='friend_requests_received', on_delete=models.CASCADE)
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Friend request from {self.from_user} to {self.to_user}"