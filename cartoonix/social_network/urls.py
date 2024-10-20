from django.urls import path
from .views import fbv

urlpatterns = [
    path('posts/', fbv.post_list, name='post_list'),
    path('posts/<int:post_id>/', fbv.post_detail, name='post_detail'),
    path('posts/<int:post_id>/comments/', fbv.comment_list, name='comment_list'),
    path('posts/<int:post_id>/like/', fbv.like_post, name='like_post'),
    path('posts/<int:post_id>/unlike/', fbv.unlike_post, name='unlike_post'),
]