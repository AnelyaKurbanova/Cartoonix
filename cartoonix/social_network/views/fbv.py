from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import FriendRequest, Post, Like, Comment, PostForm, Profile, ProfileForm
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
from django.http import JsonResponse
from django.contrib.auth.models import User


def login_page(request):
    if request.method == 'POST':
        username = request.POST['username']  # Используем request.POST
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)  # Логиним пользователя в сессии
            return redirect('home')  # Перенаправляем на главную страницу
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')

@api_view(['GET', 'POST'])
def post_list(request):
    if request.method == 'GET':
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def post_detail(request, post_id):
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = PostSerializer(post)
        return Response(status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        if post.author != request.user:
            return Response({"error": "You can only edit your own posts."}, status=status.HTTP_403_FORBIDDEN)
        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if post.author != request.user:
            return Response({"error": "You can only delete your own posts."}, status=status.HTTP_403_FORBIDDEN)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def comment_list(request, post_id):
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        comments = post.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user, post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@login_required(login_url='/social_network/login/')
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user  # Получаем текущего пользователя
    liked = False
    
    # Проверяем, есть ли уже лайк от пользователя для данного поста
    like, created = Like.objects.get_or_create(post=post, user=user)

    if not created:
        # Если лайк уже существует, удаляем его
        like.delete()
        liked = False
    else:
        # Лайк создан
        liked = True

    data = {
        'liked': liked,
        'total_likes': post.total_likes(),
    }
    return JsonResponse(data)


def register_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful. Please log in.')
            return redirect('login_page')  # Перенаправляем на страницу логина
        else:
            messages.error(request, 'Registration failed. Please try again.')
    else:
        form = UserCreationForm()
    
    return render(request, 'register.html', {'form': form})
    
@login_required(login_url='/social_network/login/')
def profile_update_view(request):
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        messages.error(request, 'Profile not found.')
        return redirect('home')

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('home')
        else:
            messages.error(request, 'Failed to update profile.')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'update_profile.html', {'form': form})


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
def send_friend_request(request, profile_id):
    try:
        to_user_profile = Profile.objects.get(pk=profile_id)
        from_user_profile = request.user.profile

        # Проверяем, не является ли это пользователь сам собой
        if from_user_profile == to_user_profile:
            return Response({"message": "You cannot add yourself as a friend"}, status=status.HTTP_400_BAD_REQUEST)

        # Проверяем, не существует ли уже запроса в друзья
        if FriendRequest.objects.filter(from_user=request.user, to_user=to_user_profile.user).exists():
            return Response({"message": "Friend request already sent"}, status=status.HTTP_400_BAD_REQUEST)

        # Создаем запрос в друзья
        friend_request = FriendRequest(from_user=request.user, to_user=to_user_profile.user)
        friend_request.save()

        return Response({"message": "Friend request sent successfully"}, status=status.HTTP_201_CREATED)
    except Profile.DoesNotExist:
        return Response({"message": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
    
@login_required
def view_friend_requests(request):
    friend_requests = FriendRequest.objects.filter(to_user=request.user, is_accepted=False)

    context = {
        'friend_requests': friend_requests,
    }
    return render(request, 'friend_requests.html', context)

@api_view(['POST'])
def accept_friend_request(request, request_id):
    try:
        friend_request = FriendRequest.objects.get(id=request_id, to_user=request.user)

        # Принимаем запрос и добавляем в друзья
        if friend_request.is_accepted is False:
            request.user.profile.friends.add(friend_request.from_user.profile)
            friend_request.from_user.profile.friends.add(request.user.profile)
            friend_request.is_accepted = True
            friend_request.save()

        return Response({"message": "Friend request accepted"}, status=status.HTTP_200_OK)
    except FriendRequest.DoesNotExist:
        return Response({"message": "Friend request not found"}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['POST'])
def reject_friend_request(request, request_id):
    try:
        friend_request = FriendRequest.objects.get(id=request_id, to_user=request.user)
        friend_request.delete()
        return Response({"message": "Friend request rejected"}, status=status.HTTP_200_OK)
    except FriendRequest.DoesNotExist:
        return Response({"message": "Friend request not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@login_required
def remove_friend(request, profile_id):
    try:
        friend_profile = Profile.objects.get(pk=profile_id)
        user_profile = request.user.profile

        if not user_profile.is_friend(friend_profile):
            return JsonResponse({"message": "You are not friends with this user"}, status=status.HTTP_400_BAD_REQUEST)

        user_profile.remove_friend(friend_profile)
        return JsonResponse({"message": "Friend removed successfully"}, status=status.HTTP_204_NO_CONTENT)
    except Profile.DoesNotExist:
        return JsonResponse({"message": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)


@login_required
def list_friends(request):
    profile = request.user.profile  # Получаем профиль текущего пользователя
    friends = profile.friends.all()  # Друзья текущего пользователя

    context = {
        'friends': friends,
        'profile': profile,  # Передаем профиль для сравнения
    }
    return render(request, 'list_friends.html', context)

@login_required(login_url='/social_network/login/')
def home(request):
    posts = Post.objects.all()  # Получаем все посты
    context = {
        'posts': posts,  # Добавляем посты в контекст
    }
    return render(request, 'home.html', context) 
    

def logout_view(request):
    logout(request)
    return redirect('login_page')

@login_required(login_url='/social_network/login/')
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)  # Добавляем request.FILES для работы с изображениями
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user  # Присваиваем текущего пользователя как автора поста
            post.save()
            messages.success(request, 'Post created successfully.')
            return redirect('home')  # Перенаправляем на главную страницу после успешного создания поста
        else:
            messages.error(request, 'Failed to create post. Please try again.')
    else:
        form = PostForm()  # Передаем пустую форму

    return render(request, 'create_post.html', {'form': form})

@login_required(login_url='/social_network/login/')
def profile_view(request, username):
    # Получаем пользователя по имени пользователя (username)
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user)

    # Проверяем, является ли текущий пользователь другом
    is_friend = request.user.profile.is_friend(profile)

    context = {
        'user_profile': profile,
        'is_friend': is_friend,  # Добавляем результат проверки в контекст
    }

    return render(request, 'profile.html', context)

@login_required(login_url='/social_network/login/')
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # Проверяем, что текущий пользователь является автором поста
    if post.author != request.user:
        messages.error(request, 'You can only edit your own posts.')
        return redirect('home')

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post updated successfully.')
            return redirect('home')
        else:
            messages.error(request, 'Failed to update post. Please try again.')
    else:
        form = PostForm(instance=post)

    return render(request, 'edit_post.html', {'form': form, 'post': post})

@login_required(login_url='/social_network/login/')
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # Проверяем, что текущий пользователь является автором поста
    if post.author != request.user:
        messages.error(request, 'You can only delete your own posts.')
        return redirect('home')

    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted successfully.')
        return redirect('home')