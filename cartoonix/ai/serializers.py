from rest_framework import serializers
from .models import VideoPrompt

class VideoPromptSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoPrompt
        fields = '__all__'

