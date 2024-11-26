from django.contrib.auth.models import User
from ai.models import VideoPrompt
from .models import Comment, Profile
from rest_framework import serializers
from .models import Post

class VideoPromptSerializer(serializers.ModelSerializer):
    class Meta:
        ref_name = "SocialNetwork_VideoPrompt"
        model = VideoPrompt
        fields = '__all__'


class PostSerializer(serializers.ModelSerializer):
    video_url = VideoPromptSerializer(required=False) 
    
    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'created_at', 'author', 'image', 'video_url']

    def create(self, validated_data):
        video_url_data = validated_data.pop('video_url', None)
        post = Post.objects.create(**validated_data)
        if video_url_data:
            video_prompt = VideoPrompt.objects.create(**video_url_data)
            post.video_url = video_prompt
            post.save()
        return post

    def update(self, instance, validated_data):
        video_url_data = validated_data.pop('video_url', None)
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.image = validated_data.get('image', instance.image)
        instance.save()

        if video_url_data:
            if instance.video_url:
                for attr, value in video_url_data.items():
                    setattr(instance.video_url, attr, value)
                instance.video_url.save()
            else:
                video_prompt = VideoPrompt.objects.create(**video_url_data)
                instance.video_url = video_prompt
                instance.save()

        return instance


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()

    class Meta:
        model = Comment
        fields = ['id', 'content', 'created_at', 'author', 'post']
        read_only_fields = ['author', 'post', 'created_at']


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        Profile.objects.create(user=user)
        return user


class ProfileSerializer(serializers.ModelSerializer):
    friends = serializers.StringRelatedField(many=True)
    class Meta:
        model = Profile
        fields = ['user', 'image', 'bio', 'created_at', 'friends']