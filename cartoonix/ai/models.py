from django.db import models

class VideoPrompt(models.Model):
    prompt = models.TextField()
    arrTitles = models.JSONField(blank=True, null=True) 
    arrImages = models.JSONField(blank=True, null=True)
    arrVideos = models.JSONField(blank=True, null=True) 
    finalVideo = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"VideoPrompt {self.prompt[:50]}... (ID: {self.id})"