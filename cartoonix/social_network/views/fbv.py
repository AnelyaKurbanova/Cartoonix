from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from rest_framework import status
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import FriendRequest, Post, Comment, PostForm, Profile, ProfileForm
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
from ..forms import UserRegisterForm, ProfileUpdateForm, CommentForm, PostForm
from django.views.decorators.csrf import csrf_exempt
import logging


def login_page(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')








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


from django.http import JsonResponse, Http404

@login_required(login_url='/social_network/login/')
def like_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        raise Http404("Post does not exist")
    
    user = request.user
    if user in post.likes.all():
        post.likes.remove(user)  # Удаляем лайк
        liked = False
    else:
        post.likes.add(user)  # Добавляем лайк
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

# @login_required
# def like_post(request, pk):
#     post = get_object_or_404(Post, pk=pk)
#     if post.likes.filter(user=request.user).exists():
#         post.likes.get(user=request.user).delete()
#     else:
#         Like.objects.create(post=post, user=request.user)
#     return redirect('post_detail', pk=pk)

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
@csrf_exempt # Обязательно для запросов DELETE без формы
def delete_profile(request):
    try:
        profile = Profile.objects.get(user=request.user)
        user = request.user
    except Profile.DoesNotExist:
        return JsonResponse({"message": "Profile not found"}, status=404)

    if request.method == 'DELETE':
        profile.delete()
        user.delete()
        return JsonResponse({"message": "Profile and user account deleted"}, status=204)

    return JsonResponse({"error": "Method not allowed"}, status=405)


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

@api_view(['POST'])
def accept_friend_request(request, request_id):
    try:
        friend_request = FriendRequest.objects.get(pk=request_id, to_user=request.user)
        from_user = friend_request.from_user

        # Добавляем пользователей друг к другу в друзья
        request.user.profile.friends.add(from_user.profile)
        from_user.profile.friends.add(request.user.profile)

        # Удаляем запрос дружбы
        friend_request.delete()

        return JsonResponse({'message': 'Friend request accepted successfully'}, status=200)
    except FriendRequest.DoesNotExist:
        return JsonResponse({'error': 'Friend request does not exist'}, status=404)
    
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
            return JsonResponse({"message": "You are not friends with this user"}, status=400)

        # Удаляем друга из списка друзей
        user_profile.friends.remove(friend_profile)
        friend_profile.friends.remove(user_profile)

        # Удаляем связанные запросы дружбы
        FriendRequest.objects.filter(from_user=request.user, to_user=friend_profile.user).delete()
        FriendRequest.objects.filter(from_user=friend_profile.user, to_user=request.user).delete()

        return JsonResponse({"message": "Friend removed successfully"}, status=200)
    except Profile.DoesNotExist:
        return JsonResponse({"message": "Profile not found"}, status=404)


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
    user_profile = get_object_or_404(Profile, user__username=username)
    friend_requests = FriendRequest.objects.filter(to_user=request.user)

    # Проверяем, есть ли запрос от текущего пользователя к отображаемому профилю
    sent_request = FriendRequest.objects.filter(from_user=request.user, to_user=user_profile.user).exists()

    context = {
        'user_profile': user_profile,
        'friend_requests': friend_requests,
        'is_friend': request.user.profile.is_friend(user_profile),
        'sent_request': sent_request,  # Отправлен ли запрос дружбы
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

    user = request.user
    user.delete()
    return redirect('register')


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

