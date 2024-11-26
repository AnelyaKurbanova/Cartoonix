from django.urls import path
from .views import fbv

urlpatterns = [
    path('home/', fbv.home, name='home'),
    path('posts/', fbv.post_list, name='post_list'),
    path('create_post/', fbv.create_post, name='create_post'),
    path('posts/<int:post_id>/', fbv.post_detail, name='post_detail'),
    path('posts/<int:post_id>/comments/', fbv.comment_list, name='comment_list'),
    path('posts/<int:post_id>/like/', fbv.like_post, name='like_post'),
    path('posts/<int:post_id>/edit/', fbv.edit_post, name='edit_post'),
    path('posts/<int:post_id>/delete/', fbv.delete_post, name='delete_post'),
    path('api/register/', fbv.register_user, name='register_user'),
    path('profile/<str:username>/', fbv.profile_view, name='profile_view'),
    path('profile/friends/', fbv.list_friends, name='list_friends'),
    path('search/', fbv.search_users, name='search_users'),
    path('api/profile/update/', fbv.profile_update_view, name='profile_update'),
    path('api/profile/delete/', fbv.delete_profile, name='delete_profile'),
    path('send_friend_request/<int:profile_id>/', fbv.send_friend_request, name='send_friend_request'),
    path('accept_friend_request/<int:request_id>/', fbv.accept_friend_request, name='accept_friend_request'),
    path('reject_friend_request/<int:request_id>/', fbv.reject_friend_request, name='reject_friend_request'),
    path('api/profile/friends/remove/<int:profile_id>/', fbv.remove_friend, name='remove_friend'),
    path('api/profile/friends/', fbv.list_friends, name='list_friends'),
    path('api/friends/', fbv.search_friends, name='search_friends'),
    path('login/', fbv.login_page, name='login_page'),
    path('logout/', fbv.logout_view, name='logout'),
]

