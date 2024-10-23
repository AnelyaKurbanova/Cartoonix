from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Post, Comment, Like

from rest_framework import serializers
from .models import Post


class VideoPromptSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoPrompt
        fields = ['id', 'prompt_text']  # Укажите необходимые поля


# class UserRegisterSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True)
#     email = serializers.EmailField()
#
#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password']
#
#     def create(self, validated_data):
#         user = User.objects.create_user(
#             username=validated_data['username'],
#             email=validated_data['email'],
#             password=validated_data['password']
#         )
#         Profile.objects.create(user=user)
#         return user
#
#
# class ProfileSerializer(serializers.ModelSerializer):
#     friends = serializers.StringRelatedField(many=True)
#     class Meta:
#         model = Profile
#         fields = ['user', 'image', 'bio', 'created_at', 'friends']
