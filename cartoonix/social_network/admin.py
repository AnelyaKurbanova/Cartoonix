from django.contrib import admin
from .models import Post, Comment

# @admin.register(Post)
# class PostAdmin(admin.ModelAdmin):
#     list_display = ('title', 'author', 'created_at')
#     search_fields = ('title', 'content')
#     prepopulated_fields = {'slug': ('title',)}

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('content', 'author', 'post', 'created_at')
    search_fields = ('content',)
