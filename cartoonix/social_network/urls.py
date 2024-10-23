from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from .views import fbv
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('', fbv.post_list, name='post_list'),
    path('post/<int:pk>/', fbv.post_detail, name='post_detail'),
    path('post/new/', fbv.post_create, name='post_create'),
    path('post/<int:pk>/comment/', fbv.add_comment, name='add_comment'),
    path('post/<int:pk>/like/', fbv.like_post, name='like_post'),
    path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/register/', fbv.register_user, name='register_user'),
    path('api/profile/update/', fbv.update_profile, name='update_profile'),
    path('api/profile/delete/', fbv.delete_profile, name='delete_profile'),
    path('api/profile/friends/add/<int:profile_id>/', fbv.add_friend, name='add_friend'),
    path('api/profile/friends/remove/<int:profile_id>/', fbv.remove_friend, name='remove_friend'),
    path('api/profile/friends/', fbv.list_friends, name='list_friends'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)