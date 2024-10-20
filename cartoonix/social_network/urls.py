from django.urls import path
from .views import fbv
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('posts/', fbv.post_list, name='post_list'),
    path('posts/<int:post_id>/', fbv.post_detail, name='post_detail'),
    path('posts/<int:post_id>/comments/', fbv.comment_list, name='comment_list'),
    path('posts/<int:post_id>/like/', fbv.like_post, name='like_post'),
    path('posts/<int:post_id>/unlike/', fbv.unlike_post, name='unlike_post'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/register/', fbv.register_user, name='register_user'),
    path('api/profile/update/', fbv.update_profile, name='update_profile'),
    path('api/profile/delete/', fbv.delete_profile, name='delete_profile'),
]