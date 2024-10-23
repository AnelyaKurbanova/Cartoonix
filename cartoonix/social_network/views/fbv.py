from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from rest_framework import status
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.decorators import api_view, login_required
from rest_framework.response import Response
from ..models import Post, Like, Comment, Profile
from ..serializers import PostSerializer, CommentSerializer,UserRegisterSerializer, ProfileSerializer
from rest_framework.permissions import IsAuthenticated
from ..forms import UserRegisterForm, ProfileUpdateForm, CommentForm, PostForm




def post_list(request):
    posts = Post.objects.all()
    return render(request, 'posts/post_list.html', {'posts': posts})

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    is_liked = False
    if post.likes.filter(user=request.user).exists():
        is_liked = True
    return render(request, 'posts/post_detail.html', {'post': post, 'is_liked': is_liked})

@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('post_detail', pk=post.pk)
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
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()
    return render(request, 'posts/create_comment.html', {'form': form})

@login_required
def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.likes.filter(user=request.user).exists():
        post.likes.get(user=request.user).delete()
    else:
        Like.objects.create(post=post, user=request.user)
    return redirect('post_detail', pk=pk)

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'social_network/register.html', {'form': form})


@login_required
def profile(request):
    if request.user.is_authenticated:
        try:
            user_profile = request.user.profile  # Получение профиля пользователя
            return render(request, 'social_network/profile.html', {'user': request.user, 'profile': user_profile})
        except Profile.DoesNotExist:
            return render(request, 'social_network/profile.html', {'message': 'Profile does not exist.'})
    else:
        return render(request, 'social_network/profile.html', {'message': 'Please log in to see your profile.'})


@login_required
def update_profile(request):
    if request.method == 'POST':
        profile_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        if profile_form.is_valid():
            profile_form.save()
            return redirect('profile')
    else:
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    return render(request, 'social_network/update_profile.html', {'profile_form': profile_form})


@login_required
def delete_profile(request):
    user = request.user
    user.delete()
    return redirect('register')


@login_required
def add_friend(request, user_id):
    friend = Profile.objects.get(user__id=user_id)
    request.user.profile.friends.add(friend)
    return redirect('profile')


@login_required
def remove_friend(request, user_id):
    friend = Profile.objects.get(user__id=user_id)
    request.user.profile.friends.remove(friend)
    return redirect('profile')


@login_required
def friends_list(request):
    friends = request.user.profile.friends.all()
    return render(request, 'social_network/friends_list.html', {'friends': friends})


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
