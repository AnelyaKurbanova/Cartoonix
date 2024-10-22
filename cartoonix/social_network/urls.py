from django.urls import path
from .views import fbv
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('posts/', fbv.post_list, name='post_list'),
    path('posts/<int:post_id>/', fbv.post_detail, name='post_detail'),
    path('posts/<int:post_id>/comments/', fbv.comment_list, name='comment_list'),
    path('posts/<int:post_id>/like/', fbv.like_post, name='like_post'),
    path('posts/<int:post_id>/unlike/', fbv.unlike_post, name='unlike_post'),
    path('register/', fbv.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='social_network/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='social_network/logout.html'), name='logout'),
    path('profile/', fbv.profile, name='profile'),
    path('profile/update/', fbv.update_profile, name='update_profile'),
    path('profile/delete/', fbv.delete_profile, name='delete_profile'),
    path('friends/add/<int:user_id>/', fbv.add_friend, name='add_friend'),
    path('friends/remove/<int:user_id>/', fbv.remove_friend, name='remove_friend'),
    path('friends/', fbv.friends_list, name='friends_list'),
]