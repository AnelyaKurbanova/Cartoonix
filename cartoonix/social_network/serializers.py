from rest_framework import serializers
from .models import Post, Comment, Like

class PostSerializer(serializers.ModelSerializer):
    total_likes = serializers.ReadOnlyField()

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'created_at', 'author', 'total_likes']
        read_only_fields = ['author', 'created_at']

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'content', 'created_at', 'author', 'post']
        read_only_fields = ['author', 'post', 'created_at']

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'user', 'post', 'created_at']
        read_only_fields = ['user', 'post', 'created_at']
