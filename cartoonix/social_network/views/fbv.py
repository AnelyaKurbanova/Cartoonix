from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import Post, Like, Comment
from ..serializers import PostSerializer, CommentSerializer
from rest_framework.permissions import IsAuthenticated


@api_view(['GET', 'POST'])
def post_list(request):
    if request.method == 'GET':
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

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
        return Response(serializer.data)

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

@api_view(['POST'])
def like_post(request, post_id):
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    like, created = Like.objects.get_or_create(post=post, user=request.user)
    if created:
        return Response({"message": "Post liked"}, status=status.HTTP_201_CREATED)
    return Response({"message": "Post already liked"}, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def unlike_post(request, post_id):
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    try:
        like = Like.objects.get(post=post, user=request.user)
        like.delete()
        return Response({"message": "Like removed"}, status=status.HTTP_204_NO_CONTENT)
    except Like.DoesNotExist:
        return Response({"message": "You haven't liked this post"}, status=status.HTTP_404_NOT_FOUND)
