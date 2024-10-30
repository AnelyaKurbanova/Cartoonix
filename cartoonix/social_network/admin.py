from django.contrib import admin
from .models import Post, Comment, Like

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at')
    search_fields = ('title', 'content')
    # prepopulated_fields = {'slug': ('title')}

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('content', 'author', 'post', 'created_at')
    search_fields = ('content',)

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')
    search_fields = ('user__username',)
