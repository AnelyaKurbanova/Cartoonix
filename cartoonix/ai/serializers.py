from rest_framework import serializers
from .models import VideoPrompt


class VideoPromptSerializer(serializers.ModelSerializer):
    class Meta:
        ref_name = "AI_VideoPrompt"
        model = VideoPrompt
        fields = '__all__'

