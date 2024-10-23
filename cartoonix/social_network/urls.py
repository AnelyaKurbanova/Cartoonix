from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from .views import fbv
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.contrib.auth import views as auth_views



urlpatterns = [

    path('home/', fbv.home, name='home'),

    path('posts/', fbv.post_list, name='post_list'),
    path('create_post/', fbv.create_post, name='create_post'),

    path('posts/<int:post_id>/', fbv.post_detail, name='post_detail'),
    path('posts/<int:post_id>/comments/', fbv.comment_list, name='comment_list'),
    path('posts/<int:post_id>/like/', fbv.like_post, name='like_post'),
    path('posts/<int:post_id>/edit/', fbv.edit_post, name='edit_post'),
    path('posts/<int:post_id>/delete/', fbv.delete_post, name='delete_post'),
    # path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/register/', fbv.register_user, name='register_user'),

    path('profile/<str:username>/', fbv.profile_view, name='profile_view'),
    path('profile/friends/', fbv.list_friends, name='list_friends'),
    path('api/profile/update/', fbv.profile_update_view, name='profile_update'),
    path('api/profile/delete/', fbv.delete_profile, name='delete_profile'),
    path('friend_requests/', fbv.view_friend_requests, name='view_friend_requests'),
    path('send_friend_request/<int:profile_id>/', fbv.send_friend_request, name='send_friend_request'),
    path('accept_friend_request/<int:request_id>/', fbv.accept_friend_request, name='accept_friend_request'),
    path('reject_friend_request/<int:request_id>/', fbv.reject_friend_request, name='reject_friend_request'),
    path('api/profile/friends/remove/<int:profile_id>/', fbv.remove_friend, name='remove_friend'),
    path('api/profile/friends/', fbv.list_friends, name='list_friends'),
    

    path('login/', fbv.login_page, name='login_page'),
    path('logout/', fbv.logout_view, name='logout'),

]

#     path('', fbv.post_list, name='post_list'),
#     path('post/<int:pk>/', fbv.post_detail, name='post_detail'),
#     path('post/new/', fbv.post_create, name='post_create'),
#     path('post/<int:pk>/comment/', fbv.add_comment, name='add_comment'),
#     path('post/<int:pk>/like/', fbv.like_post, name='like_post'),
#     path('register/', fbv.register, name='register'),
#     path('login/', auth_views.LoginView.as_view(template_name='social_network/login.html'), name='login'),
#     path('logout/', auth_views.LogoutView.as_view(template_name='social_network/logout.html'), name='logout'),
#     path('profile/', fbv.profile, name='profile'),
#     path('profile/update/', fbv.update_profile, name='update_profile'),
#     path('profile/delete/', fbv.delete_profile, name='delete_profile'),
#     path('friends/add/<int:user_id>/', fbv.add_friend, name='add_friend'),
#     path('friends/remove/<int:user_id>/', fbv.remove_friend, name='remove_friend'),
#     path('friends/', fbv.friends_list, name='friends_list'),
# ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


