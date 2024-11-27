from django.db import models


class VideoPrompt(models.Model):
    CATEGORY_CHOICES = [
        ('comedy', 'Comedy'),
        ('tragedy', 'Tragedy'),
        ('humor', 'Humor'),
        ('romance', 'Romance'),
        ('horror', 'Horror'),
    ]
    
    prompt = models.TextField()
    arrTitles = models.JSONField(blank=True, null=True) 
    arrImages = models.JSONField(blank=True, null=True)
    arrVideos = models.JSONField(blank=True, null=True) 
    finalVideo = models.URLField(blank=True, null=True)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='comedy')
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"VideoPrompt {self.prompt[:50]}... (ID: {self.id})"