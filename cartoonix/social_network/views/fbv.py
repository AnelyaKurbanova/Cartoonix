from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404, render
from rest_framework import status

from ..forms import CommentForm, PostForm
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import Post, Like, Comment, Profile
from rest_framework.permissions import IsAuthenticated

from ..serializers import UserRegisterSerializer, ProfileSerializer


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

@api_view(['POST'])
def register_user(request):
    if request.method == 'POST':
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH'])
def update_profile(request):
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        return Response({"message": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PATCH':
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_profile(request):
    try:
        profile = Profile.objects.get(user=request.user)
        user = request.user
    except Profile.DoesNotExist:
        return Response({"message": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        profile.delete()
        user.delete()
        return Response({"message": "Profile and user account deleted"}, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
def add_friend(request, profile_id):
    try:
        friend_profile = Profile.objects.get(pk=profile_id)
        user_profile = request.user.profile

        if user_profile == friend_profile:
            return Response({"message": "You cannot add yourself as a friend"}, status=status.HTTP_400_BAD_REQUEST)

        if user_profile.is_friend(friend_profile):
            return Response({"message": "You are already friends"}, status=status.HTTP_400_BAD_REQUEST)

        user_profile.add_friend(friend_profile)
        return Response({"message": "Friend added successfully"}, status=status.HTTP_201_CREATED)
    except Profile.DoesNotExist:
        return Response({"message": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
def remove_friend(request, profile_id):
    try:
        friend_profile = Profile.objects.get(pk=profile_id)
        user_profile = request.user.profile

        if not user_profile.is_friend(friend_profile):
            return Response({"message": "You are not friends with this user"}, status=status.HTTP_400_BAD_REQUEST)

        user_profile.remove_friend(friend_profile)
        return Response({"message": "Friend removed successfully"}, status=status.HTTP_204_NO_CONTENT)
    except Profile.DoesNotExist:
        return Response({"message": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def list_friends(request):
    user_profile = request.user.profile
    serializer = ProfileSerializer(user_profile)
    return Response(serializer.data['friends'])
