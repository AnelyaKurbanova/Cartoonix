from django.contrib.auth.models import User, AbstractUser
from django.db import models
from PIL import Image
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from ai.models import VideoPrompt
from django import forms
from django.dispatch import receiver


class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default_post.jpg', upload_to='post_pics')

    video_url = models.OneToOneField(
        VideoPrompt,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )


    def __str__(self):
        return self.title

    def total_likes(self):
        return self.likes.count()
    
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'image']

    def is_liked_by_user(self, user):
        return self.likes.filter(user=user).exists()


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

class Like(models.Model):
    post = models.ForeignKey(Post, related_name='likes', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='likes', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')

    def __str__(self):
        return f"Like by {self.user} on {self.post}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    friends = models.ManyToManyField('self', symmetrical=False, related_name='user_friends', blank=True)
    image = models.ImageField(upload_to='profile_images/', blank=True, null=True)


    def __str__(self):
        return f'{self.user.username} Profile'


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.image.path)
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)

    def add_friend(self, profile):
        self.friends.add(profile)
        self.save()

    def remove_friend(self, profile):
        self.friends.remove(profile)
        self.save()

    def is_friend(self, profile):
        return profile in self.friends.all()

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image', 'bio']
    
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='friend_requests_sent', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='friend_requests_received', on_delete=models.CASCADE)
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Friend request from {self.from_user} to {self.to_user}"

