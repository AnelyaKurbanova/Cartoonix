from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.db.models import Q
from django.views.decorators.http import require_POST
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import FriendRequest, Post, Comment, PostForm, Profile, ProfileForm
from ..models import FriendRequest, Post, Comment, PostForm, Profile, ProfileForm, Notification
from ..serializers import PostSerializer, CommentSerializer, UserRegisterSerializer, ProfileSerializer
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import logout
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from django.http import JsonResponse, Http404
from django.http import JsonResponse
from django.contrib.auth.models import User
from ..forms import UserRegisterForm, ProfileUpdateForm, CommentForm, PostForm
from django.views.decorators.csrf import csrf_exempt
import logging
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..signals import friend_request_sent, friend_request_accepted, post_liked, comment_added

logger = logging.getLogger('api_logger')

def login_page(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            logger.info(f"User {username} logged in successfully.")
            return redirect('home')
        else:
            logger.warning(f"Failed login attempt for username: {username}.")
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')



@swagger_auto_schema(
    method='get',
    responses={200: PostSerializer(many=True)},
    operation_description="Retrieve a list of posts."
)
@swagger_auto_schema(
    method='post',
    request_body=PostSerializer,
    responses={201: PostSerializer, 400: "Bad Request"},
    operation_description="Create a new post."
)
@api_view(['GET', 'POST'])


def post_list(request):
    if request.method == 'GET':
        posts = Post.objects.all()
        logger.info(f"User {request.user} accessed the post list.")
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            logger.info(f"User {request.user} created a new post with title: {serializer.validated_data['title']}.")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f"User {request.user} failed to create a post. Errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='get',
    responses={200: PostSerializer, 404: "Not Found"},
    operation_description="Retrieve a specific post by id."
)
@swagger_auto_schema(
    method='put',
    request_body=PostSerializer,
    responses={200: PostSerializer, 400: "Bad Request", 403: "Forbidden"},
    operation_description="Update an existing post."
)
@swagger_auto_schema(
    method='delete',
    responses={204: "No Content", 403: "Forbidden"},
    operation_description="Delete a post by id."
)
@api_view(['GET', 'PUT', 'DELETE'])
def post_detail(request, post_id):
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        logger.error(f"Post with ID {post_id} not found.")
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        logger.info(f"User {request.user} accessed details of post {post_id}.")
        serializer = PostSerializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        if post.author != request.user:
            logger.warning(f"User {request.user} attempted to edit post {post_id} without permission.")
            return Response({"error": "You can only edit your own posts."}, status=status.HTTP_403_FORBIDDEN)
        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"User {request.user} updated post {post_id}.")
            return Response(serializer.data)
        logger.error(f"User {request.user} failed to update post {post_id}. Errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if post.author != request.user:
            logger.warning(f"User {request.user} attempted to delete post {post_id} without permission.")
            return Response({"error": "You can only delete your own posts."}, status=status.HTTP_403_FORBIDDEN)
        post.delete()
        logger.info(f"User {request.user} deleted post {post_id}.")
        return Response(status=status.HTTP_204_NO_CONTENT)

@swagger_auto_schema(
    method='get',
    responses={200: CommentSerializer(many=True), 404: "Not Found"},
    operation_description="Retrieve comments for a specific post."
)
@swagger_auto_schema(
    method='post',
    request_body=CommentSerializer,
    responses={201: CommentSerializer, 400: "Bad Request"},
    operation_description="Add a comment to a post."
)

@api_view(['GET', 'POST'])
def comment_list(request, post_id):
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        logger.error(f"Post with ID {post_id} not found for commenting.")
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        comments = post.comments.all()
        logger.info(f"User {request.user} accessed comments for post {post_id}.")
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user, post=post)
            logger.info(f"User {request.user} added a comment to post {post_id}.")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f"User {request.user} failed to add comment to post {post_id}. Errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@login_required(login_url='/social_network/login/')
def like_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        logger.error(f"Post with ID {post_id} not found for liking.")
        raise Http404("Post does not exist")

    user = request.user
    if user in post.likes.all():
        post.likes.remove(user)
        logger.info(f"User {user} unliked post {post_id}.")
        liked = False
    else:
        post.likes.add(user)
        logger.info(f"User {user} liked post {post_id}.")
        liked = True

    if liked:
        post_liked.send(sender=Post, post=post, user=request.user)

    data = {
        'liked': liked,
        'total_likes': post.total_likes(),
    }
    return JsonResponse(data)


def register_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            logger.info(f"User {user.username} registered successfully.")
            messages.success(request, 'Registration successful. Please log in.')
            return redirect('login_page')  # Перенаправляем на страницу логина
        else:
            logger.warning("Failed registration attempt. Errors: %s", form.errors)
            messages.error(request, 'Registration failed. Please try again.')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

@login_required(login_url='/social_network/login/')
def profile_update_view(request):
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        logger.error(f"Profile for user {request.user.username} not found.")
        messages.error(request, 'Profile not found.')
        return redirect('home')

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            logger.info(f"User {request.user.username} updated their profile.")
            messages.success(request, 'Profile updated successfully.')
            return redirect('home')
        else:
            logger.warning(f"User {request.user.username} failed to update profile. Errors: {form.errors}")
            messages.error(request, 'Failed to update profile.')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'update_profile.html', {'form': form})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    is_liked = False
    if post.likes.filter(user=request.user).exists():
        is_liked = True
    logger.info(f"User {request.user} viewed post {pk}. Liked: {is_liked}")
    return render(request, 'posts/post_detail.html', {'post': post, 'is_liked': is_liked})

@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            logger.info(f"User {request.user.username} created a post with title: {post.title}.")
            return redirect('post_detail', pk=post.pk)
        else:
            logger.warning(f"User {request.user.username} failed to create a post. Errors: {form.errors}")
    else:
        form = PostForm()
    return render(request, 'posts/create_post.html', {'form': form})

@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            logger.info(f"User {request.user.username} added a comment to post {post.pk}.")
            return redirect('post_detail', pk=post.pk)
        else:
            logger.warning(f"User {request.user.username} failed to add a comment. Errors: {form.errors}")
    else:
        form = CommentForm()
    comment_added.send(sender=Comment, post=post, user=request.user, comment=form)
    return render(request, 'posts/create_comment.html', {'form': form})

# @login_required
# def like_post(request, pk):
#     post = get_object_or_404(Post, pk=pk)
#     if post.likes.filter(user=request.user).exists():
#         post.likes.get(user=request.user).delete()
#     else:
#         Like.objects.create(post=post, user=request.user)
#     return redirect('post_detail', pk=pk)



@login_required
def profile(request):
    if request.user.is_authenticated:
        try:
            user_profile = request.user.profile  # Получение профиля пользователя
            logger.info(f"User {request.user.username} accessed their profile.")
            return render(request, 'social_network/profile.html', {'user': request.user, 'profile': user_profile})
        except Profile.DoesNotExist:
            logger.error(f"Profile for user {request.user.username} does not exist.")
            return render(request, 'social_network/profile.html', {'message': 'Profile does not exist.'})
    else:
        return render(request, 'social_network/profile.html', {'message': 'Please log in to see your profile.'})


@login_required
def update_profile(request):
    if request.method == 'POST':
        profile_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        if profile_form.is_valid():
            profile_form.save()
            logger.info(f"User {request.user.username} updated their profile.")
            return redirect('profile')
        else:
            logger.warning(f"User {request.user.username} failed to update their profile. Errors: {profile_form.errors}")
    else:
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    return render(request, 'social_network/update_profile.html', {'profile_form': profile_form})


@login_required
@csrf_exempt
def delete_profile(request):
    try:
        profile = Profile.objects.get(user=request.user)
        user = request.user
    except Profile.DoesNotExist:
        logger.error(f"Profile for user {request.user.username} not found.")
        return JsonResponse({"message": "Profile not found"}, status=404)

    if request.method == 'DELETE':
        profile.delete()
        user.delete()
        logger.info(f"User {user.username} and their profile have been deleted.")
        return JsonResponse({"message": "Profile and user account deleted"}, status=204)

    logger.warning(f"User {request.user.username} attempted an invalid method on profile deletion.")
    return JsonResponse({"error": "Method not allowed"}, status=405)

@swagger_auto_schema(
    method='post',
    responses={201: "Friend request sent successfully", 400: "Bad Request"},
    operation_description="Send a friend request to another user."
)
@csrf_exempt
@api_view(['POST'])
@login_required
def send_friend_request(request, profile_id):
    try:
        to_user_profile = Profile.objects.get(pk=profile_id)
        from_user_profile = request.user.profile

        if from_user_profile == to_user_profile:
            return JsonResponse({"message": "You cannot add yourself as a friend"}, status=400)

        if FriendRequest.objects.filter(from_user=request.user, to_user=to_user_profile.user).exists():
            return JsonResponse({"message": "Friend request already sent"}, status=400)

        friend_request = FriendRequest(from_user=request.user, to_user=to_user_profile.user)
        friend_request.save()

        friend_request_sent.send(sender=FriendRequest, from_user=request.user, to_user=to_user_profile.user)

        return Response({"message": "Friend request sent successfully"}, status=status.HTTP_201_CREATED)
        return JsonResponse({"message": "Friend request sent successfully"}, status=201)
    except Profile.DoesNotExist:
        return JsonResponse({"message": "Profile not found"}, status=404)



@swagger_auto_schema(
    method='post',
    responses={200: "Friend request accepted", 404: "Not Found"},
    operation_description="Accept a received friend request."
)
@api_view(['POST'])
@login_required
def accept_friend_request(request, request_id):
    try:
        logger.info(f"User {request.user.username} is accepting a friend request with ID {request_id}")

        # Находим заявку на добавление в друзья
        friend_request = FriendRequest.objects.get(pk=request_id, to_user=request.user)
        from_user = friend_request.from_user

        request.user.profile.friends.add(from_user.profile)
        from_user.profile.friends.add(request.user.profile)

        friend_request_accepted.send(sender=FriendRequest, from_user=from_user, to_user=request.user)

        # Удаляем запрос дружбы
        friend_request.delete()

        logger.info(f"User {request.user.username} and {from_user.username} are now friends.")

        return JsonResponse({'message': 'Friend request accepted successfully'}, status=200)
    except FriendRequest.DoesNotExist:
        # Логируем ошибку, если заявка не найдена
        logger.error(f"Friend request with ID {request_id} not found for user {request.user.username}.")
        return JsonResponse({'error': 'Friend request does not exist'}, status=404)

@swagger_auto_schema(
    method='post',
    responses={200: "Friend request rejected", 404: "Not Found"},
    operation_description="Reject a received friend request."
)

@api_view(['POST'])
@login_required
def reject_friend_request(request, request_id):
    try:
        logger.info(f"User {request.user.username} is rejecting a friend request with ID {request_id}")

        # Находим заявку на добавление в друзья
        friend_request = FriendRequest.objects.get(id=request_id, to_user=request.user)
        friend_request.delete()

        logger.info(f"User {request.user.username} rejected a friend request with ID {request_id}.")

        return JsonResponse({"message": "Friend request rejected"}, status=200)
    except FriendRequest.DoesNotExist:
        logger.error(f"Friend request with ID {request_id} not found for user {request.user.username}.")
        return JsonResponse({"message": "Friend request not found"}, status=404)

@swagger_auto_schema(
    method='delete',
    responses={200: "Friend removed successfully", 400: "Bad Request", 404: "Not Found"},
    operation_description="Remove a user from friends."
)
@api_view(['DELETE'])
@login_required
def remove_friend(request, profile_id):
    try:
        friend_profile = Profile.objects.get(pk=profile_id)
        user_profile = request.user.profile

        if not user_profile.is_friend(friend_profile):
            logger.warning(f"User {request.user.username} attempted to remove a non-existent friend relationship with profile ID {profile_id}.")
            return JsonResponse({"message": "You are not friends with this user"}, status=400)

        # Удаляем друга из списка друзей
        user_profile.friends.remove(friend_profile)
        friend_profile.friends.remove(user_profile)

        # Удаляем связанные запросы дружбы
        FriendRequest.objects.filter(from_user=request.user, to_user=friend_profile.user).delete()
        FriendRequest.objects.filter(from_user=friend_profile.user, to_user=request.user).delete()

        logger.info(f"User {request.user.username} removed friend {friend_profile.user.username}.")
        return JsonResponse({"message": "Friend removed successfully"}, status=200)
    except Profile.DoesNotExist:
        logger.error(f"Profile with ID {profile_id} not found while attempting to remove friend.")
        return JsonResponse({"message": "Profile not found"}, status=404)


@login_required
def list_friends(request):
    profile = request.user.profile
    search_query = request.GET.get('search', '').strip()
    friends = profile.friends.all()

    logger.info(f"User {request.user.username} is viewing their friends list with {friends.count()} friends.")

    # Получаем IDs пользователей, которым отправлены заявки
    friend_requests_sent = FriendRequest.objects.filter(from_user=request.user).values_list('to_user__id', flat=True)
    logger.info(f"User {request.user.username} has sent friend requests to {len(friend_requests_sent)} users.")

    # Получаем объекты заявок в друзья, которые мы получили
    friend_requests_received = FriendRequest.objects.filter(to_user=request.user)
    logger.info(f"User {request.user.username} has received {friend_requests_received.count()} friend requests.")

    if search_query:
        # Ищем пользователей по имени пользователя, исключая самого себя
        users = User.objects.filter(username__icontains=search_query).exclude(id=request.user.id)
        logger.info(f"User {request.user.username} performed a search with query '{search_query}', found {users.count()} users.")
    else:
        users = User.objects.none()
        logger.info(f"User {request.user.username} performed an empty search.")

    # Пользователи, которые не являются друзьями и не являются текущим пользователем
    non_friends = users.exclude(profile__in=friends)
    logger.info(f"Found {non_friends.count()} users who are not friends.")

    return render(request, 'list_friends.html', {
        'friends': friends,
        'non_friends': non_friends,
        'friend_requests_sent': friend_requests_sent,
        'friend_requests_received': friend_requests_received,
        'search_query': search_query,
    })

@login_required
def search_friends(request):
    search_query = request.GET.get('search', '')

    logger.info(f"User {request.user.username} started a search for: {search_query}")

    # Ищем пользователей, чьи имена содержат поисковый запрос
    if search_query:
        users = User.objects.filter(username__icontains=search_query)
        logger.info(f"Found {users.count()} users matching the search query.")
    else:
        users = User.objects.all()
        logger.info("No search query provided, returning all users.")

    # Получаем всех друзей пользователя
    profile = request.user.profile
    friends = profile.friends.all()

    logger.info(f"User {request.user.username} has {friends.count()} friends.")

    # Получаем пользователей, которые не в друзьях
    non_friends = [user for user in users if user.profile not in friends]
    logger.info(f"Found {len(non_friends)} non-friends for user {request.user.username}.")

    return render(request, 'list_friends.html', {
        'friends': friends,
        'non_friends': non_friends
    })


@login_required(login_url='/social_network/login/')
def home(request):
    posts = Post.objects.all()
    logger.info(f"User {request.user.username} accessed the home page and viewed {posts.count()} posts.")
    return render(request, 'home.html', {'posts': posts})


def logout_view(request):
    logger.info(f"User {request.user.username} logged out.")
    logout(request)
    return redirect('login_page')

@login_required(login_url='/social_network/login/')
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            logger.info(f"User {request.user.username} created a post with title: {post.title}.")
            messages.success(request, 'Post created successfully.')
            return redirect('home')
        else:
            logger.warning(f"User {request.user.username} failed to create a post. Errors: {form.errors}")
            messages.error(request, 'Failed to create post. Please try again.')
    else:
        form = PostForm()

    return render(request, 'create_post.html', {'form': form})

@login_required(login_url='/social_network/login/')
def profile_view(request, username):
    user_profile = get_object_or_404(Profile, user__username=username)
    friend_requests = FriendRequest.objects.filter(to_user=request.user)

    sent_request = FriendRequest.objects.filter(from_user=request.user, to_user=user_profile.user).exists()
    logger.info(f"User {request.user.username} viewed the profile of {username}. Sent request: {sent_request}, Is friend: {request.user.profile.is_friend(user_profile)}")

    return render(request, 'profile.html', {
        'user_profile': user_profile,
        'friend_requests': friend_requests,
        'is_friend': request.user.profile.is_friend(user_profile),
        'sent_request': sent_request,
    })


@login_required(login_url='/social_network/login/')
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # Проверяем, что текущий пользователь является автором поста
    if post.author != request.user:
        logger.warning(f"User {request.user.username} attempted to edit post {post_id} without permission.")
        messages.error(request, 'You can only edit your own posts.')
        return redirect('home')

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            logger.info(f"User {request.user.username} successfully updated post {post_id} with title: {post.title}.")
            messages.success(request, 'Post updated successfully.')
            return redirect('home')
        else:
            logger.warning(f"User {request.user.username} failed to update post {post_id}. Errors: {form.errors}")
            messages.error(request, 'Failed to update post. Please try again.')
    else:
        form = PostForm(instance=post)

    logger.info(f"User {request.user.username} accessed the edit page for post {post_id}.")
    return render(request, 'edit_post.html', {'form': form, 'post': post})

@login_required(login_url='/social_network/login/')
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # Проверяем, что текущий пользователь является автором поста
    if post.author != request.user:
        logger.warning(f"User {request.user.username} attempted to delete post {post_id} without permission.")
        messages.error(request, 'You can only delete your own posts.')
        return redirect('home')

    if request.method == 'POST':
        logger.info(f"User {request.user.username} deleted post {post_id} with title: {post.title}.")
        post.delete()
        messages.success(request, 'Post deleted successfully.')
        return redirect('home')

    logger.warning(f"User {request.user.username} accessed the delete page for post {post_id} with an invalid method.")
    return redirect('home')


# @login_required
# def remove_friend(request, user_id):
#     friend = Profile.objects.get(user__id=user_id)
#     request.user.profile.friends.remove(friend)
#     return redirect('profile')


# @api_view(['POST'])
# def register_user(request):
#     if request.method == 'POST':
#         form = UserRegisterForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             return redirect('profile', username=user.username)
#     else:
#         form = UserRegisterForm()
#     return render(request, 'social_network/register.html', {'form': form})
#
#
# def login_view(request):
#     if request.method == 'POST':
#         form = AuthenticationForm(request, data=request.POST)
#         if form.is_valid():
#             username = form.cleaned_data.get('username')
#             password = form.cleaned_data.get('password')
#             user = authenticate(username=username, password=password)
#             if user is not None:
#                 return redirect('profile', username=user.username)
#     else:
#         form = AuthenticationForm()
#     return render(request, 'social_network/login.html', {'form': form})
#
#
# def profile(request, username):
#     user = get_object_or_404(User, username=username)
#     return render(request, 'social_network/profile.html', {'user': user})
#
#
#
# def update_profile(request, username):
#     profile = get_object_or_404(Profile, user=request.user)
#
#     if request.method == 'POST':
#         form = ProfileForm(request.POST, instance=profile)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Your profile was updated successfully!')
#             return redirect('profile', username=request.user.username)
#     else:
#         form = ProfileForm(instance=profile)
#
#     return render(request, 'social_network/update_profile.html', {'form': form})
#
#
# @login_required
# def delete_profile(request):
#     user = request.user
#     profile = get_object_or_404(Profile, user=request.user)
#
#     if request.method == 'POST':
#         profile.delete()
#         user.delete()
#         messages.success(request, 'Your profile and account were deleted successfully.')
#         return redirect('register_user')  # Redirect to homepage or any other page
#
#
#
# @login_required
# def add_friend(request, profile_id):
#     friend_profile = get_object_or_404(Profile, pk=profile_id)
#     user_profile = request.user.profile
#
#     if user_profile == friend_profile:
#         messages.error(request, "You cannot add yourself as a friend.")
#         return redirect('profile', username=user_profile.user.username)
#
#     if friend_profile in user_profile.friends.all():
#         messages.error(request, "You are already friends.")
#         return redirect('profile', username=user_profile.user.username)
#
#     user_profile.friends.add(friend_profile)
#     messages.success(request, "Friend added successfully!")
#     return redirect('profile', username=user_profile.user.username)
#
#
# @login_required
# def remove_friend(request, profile_id):
#     friend_profile = get_object_or_404(Profile, pk=profile_id)
#     user_profile = request.user.profile
#
#     if friend_profile not in user_profile.friends.all():
#         messages.error(request, "You are not friends with this user.")
#         return redirect('profile', username=user_profile.user.username)
#
#     user_profile.friends.remove(friend_profile)
#     messages.success(request, "Friend removed successfully.")
#     return redirect('profile', username=user_profile.user.username)
#
#
# @login_required
# def list_friends(request):
#     user_profile = request.user.profile
#     friends = user_profile.friends.all()
#     return render(request, 'social_network/friends_list.html', {'friends': friends})

# @api_view(['PATCH'])
# def update_profile(request):
#     try:
#         profile = Profile.objects.get(user=request.user)
#     except Profile.DoesNotExist:
#         return Response({"message": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
#
#     if request.method == 'PATCH':
#         serializer = ProfileSerializer(profile, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({"message": "Profile updated successfully"}, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# @api_view(['DELETE'])
# def delete_profile(request):
#     try:
#         profile = Profile.objects.get(user=request.user)
#         user = request.user
#     except Profile.DoesNotExist:
#         return Response({"message": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
#
#     if request.method == 'DELETE':
#         profile.delete()
#         user.delete()
#         return Response({"message": "Profile and user account deleted"}, status=status.HTTP_204_NO_CONTENT)
#
#
# @api_view(['POST'])
# def add_friend(request, profile_id):
#     try:
#         friend_profile = Profile.objects.get(pk=profile_id)
#         user_profile = request.user.profile
#
#         if user_profile == friend_profile:
#             return Response({"message": "You cannot add yourself as a friend"}, status=status.HTTP_400_BAD_REQUEST)
#
#         if user_profile.is_friend(friend_profile):
#             return Response({"message": "You are already friends"}, status=status.HTTP_400_BAD_REQUEST)
#
#         user_profile.add_friend(friend_profile)
#         return Response({"message": "Friend added successfully"}, status=status.HTTP_201_CREATED)
#     except Profile.DoesNotExist:
#         return Response({"message": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
#
#
# @api_view(['DELETE'])
# def remove_friend(request, profile_id):
#     try:
#         friend_profile = Profile.objects.get(pk=profile_id)
#         user_profile = request.user.profile
#
#         if not user_profile.is_friend(friend_profile):
#             return Response({"message": "You are not friends with this user"}, status=status.HTTP_400_BAD_REQUEST)
#
#         user_profile.remove_friend(friend_profile)
#         return Response({"message": "Friend removed successfully"}, status=status.HTTP_204_NO_CONTENT)
#     except Profile.DoesNotExist:
#         return Response({"message": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
#
#
# @api_view(['GET'])
# def list_friends(request):
#     user_profile = request.user.profile
#     serializer = ProfileSerializer(user_profile)
#     return Response(serializer.data['friends'])

@swagger_auto_schema(
    method='get',
    operation_description="Retrieve unread notifications for the authenticated user.",
    responses={
        200: openapi.Response(
            description="List of unread notifications.",
            examples={
                "application/json": {
                    "notifications": [
                        {
                            "id": 1,
                            "actor": "john_doe",
                            "verb": "sent you a friend request",
                            "timestamp": "2024-11-26 12:34:56",
                        },
                    ]
                }
            }
        ),
        401: openapi.Response(description="Unauthorized"),
    },
    security=[{'Token': []}],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@login_required
def get_notifications(request):
    """
        Retrieve unread notifications for the authenticated user.

        Returns a list of unread notifications with details.
    """
    notifications = request.user.notifications.filter(read=False)
    data = {
        'notifications': [
            {
                'id': n.id,
                'actor': n.actor.username,
                'verb': n.verb,
                'target': str(n.target) if n.target else None,
                'timestamp': n.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            }
            for n in notifications
        ]
    }
    logger.info(f"User {request.user.username} retrieved notifications.")
    return JsonResponse(data)


notification_id_param = openapi.Parameter(
    'notification_id',
    openapi.IN_PATH,
    description="ID of the notification to mark as read",
    type=openapi.TYPE_INTEGER,
)


@swagger_auto_schema(
    method='post',
    operation_description="Mark a specific notification as read.",
    responses={
        200: openapi.Response(
            description="Notification marked as read.",
            examples={"application/json": {"success": True}}
        ),
        404: openapi.Response(
            description="Notification not found.",
            examples={"application/json": {"success": False}}
        ),
        401: openapi.Response(description="Unauthorized"),
    },
    manual_parameters=[notification_id_param],
    security=[{'Token': []}],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@login_required
@require_POST
def mark_notification_as_read(request, notification_id):
    """
        Mark a specific notification as read.

        Parameters:
        - notification_id (int): ID of the notification to mark as read.

        Returns a success message if the operation was successful.
    """
    try:
        notification = Notification.objects.get(id=notification_id, recipient=request.user)
        notification.read = True
        notification.save()
        logger.info(f"Notification {notification_id} marked as read by user {request.user.username}.")
        return JsonResponse({'success': True})
    except Notification.DoesNotExist:
        logger.warning(f"Notification {notification_id} not found for user {request.user.username}.")
        return JsonResponse({'success': False}, status=404)


@login_required
def search_users(request):
    query = request.GET.get('q', '')
    users = User.objects.filter(Q(username__icontains=query) | Q(profile__bio__icontains=query)).exclude(id=request.user.id)

    user_statuses = []
    for user in users:
        status = {
            'user': user,
            'is_friend': user.profile in request.user.profile.friends.all(),
            'request_sent': FriendRequest.objects.filter(from_user=request.user, to_user=user).exists()
        }
        user_statuses.append(status)

    return render(request, 'search_users.html', {
        'query': query,
        'user_statuses': user_statuses
    })

