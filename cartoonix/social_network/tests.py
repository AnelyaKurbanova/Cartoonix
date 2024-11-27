from bs4 import BeautifulSoup
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Post, Comment, Profile, FriendRequest
from .serializers import PostSerializer


class LoginPageTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('login_page')
        self.home_url = reverse('home')
        self.username = 'testuser'
        self.password = 'securepassword'
        self.user = User.objects.create_user(username=self.username, password=self.password)

    def test_login_page_renders_correctly(self):
        """Test that the login page renders successfully for a GET request."""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_successful_login(self):
        """Test that a user can log in with valid credentials."""
        response = self.client.post(self.login_url, {
            'username': self.username,
            'password': self.password
        })
        self.assertRedirects(response, self.home_url)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_failed_login(self):
        """Test that a user cannot log in with invalid credentials."""
        response = self.client.post(self.login_url, {
            'username': self.username,
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertContains(response, 'Invalid username or password.')


class PostListTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.client.login(username="testuser", password="password123")

        self.post1 = Post.objects.create(title="Test Post 1", content="Content 1", author=self.user)
        self.post2 = Post.objects.create(title="Test Post 2", content="Content 2", author=self.user)

        self.url = '/social_network/posts/'

    def test_get_posts(self):
        """Test GET request to fetch all posts."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        self.assertEqual(response.data, serializer.data)

    def test_create_post_success(self):
        """Test POST request to create a new post with valid data."""
        data = {
            "title": "New Post",
            "content": "New Content",
            "author": self.user.id
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        post = Post.objects.get(title="New Post")
        self.assertEqual(post.content, "New Content")
        self.assertEqual(post.author, self.user)

    def test_create_post_invalid(self):
        """Test POST request with invalid data."""
        data = {
            "title": "",
            "content": "Invalid Content",

        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)


class CommentListTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.client.login(username="testuser", password="password123")

        self.post = Post.objects.create(title="Test Post", content="Test Content", author=self.user)

        self.url = f'/social_network/posts/{self.post.id}/comments/'

    def test_get_comments(self):
        """Test GET request to fetch all comments for a post."""
        Comment.objects.create(content="Test Comment 1", author=self.user, post=self.post)
        Comment.objects.create(content="Test Comment 2", author=self.user, post=self.post)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['content'], "Test Comment 1")
        self.assertEqual(response.data[1]['content'], "Test Comment 2")

    def test_get_comments_post_not_found(self):
        """Test GET request when the post does not exist."""
        invalid_url = '/social_network/posts/9999/comments/'
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_comment(self):
        """Test POST request to add a comment."""
        self.client.login(username="testuser", password="password123")
        data = {
            "content": "This is a new comment."
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        comment = Comment.objects.last()
        self.assertEqual(comment.content, "This is a new comment.")
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.post, self.post)

    def test_post_comment_missing_content(self):
        """Test POST request with missing content in the comment."""
        self.client.login(username="testuser", password="password123")
        data = {}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("content", response.data)

    def test_post_comment_post_not_found(self):
        """Test POST request when the post does not exist."""
        invalid_url = '/social_network/posts/9999/comments/'
        data = {"content": "This should fail."}
        response = self.client.post(invalid_url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class LikePostTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.client.login(username="testuser", password="password123")

        self.post = Post.objects.create(title="Test Post", content="Test Content", author=self.user)

        self.url = reverse('like_post', args=[self.post.id])

    def test_like_post(self):
        """Test liking a post."""
        self.client.login(username="testuser", password="password123")

        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertTrue(data['liked'])
        self.assertEqual(data['total_likes'], 1)

        self.assertIn(self.user, self.post.likes.all())

    def test_unlike_post(self):
        """Test unliking a post."""
        self.client.login(username="testuser", password="password123")
        self.client.post(self.url)

        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertFalse(data['liked'])
        self.assertEqual(data['total_likes'], 0)

        self.assertNotIn(self.user, self.post.likes.all())

    def test_like_post_not_found(self):
        """Test liking a post that doesn't exist."""
        invalid_url = reverse('like_post', args=[9999])
        self.client.login(username="testuser", password="password123")

        response = self.client.post(invalid_url)
        self.assertEqual(response.status_code, 404)


class RegisterUserTests(TestCase):
    def test_register_user_success(self):
        """Test successful user registration."""
        url = reverse('register_user')
        data = {
            'username': 'testuser',
            'password1': 'admin123$',
            'password2': 'admin123$'
        }

        response = self.client.post(url, data)

        self.assertRedirects(response, reverse('login_page'))

    def test_register_user_invalid(self):
        """Test registration with invalid data (passwords don't match)."""
        url = reverse('register_user')
        data = {
            'username': 'testuser',
            'password1': 'password123',
            'password2': 'wrongpassword'
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 200)

        self.assertIn("Registration failed. Please try again.", response.content.decode())

        self.assertFalse(User.objects.filter(username='testuser').exists())


class ProfileUpdateViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')

        self.profile, created = Profile.objects.get_or_create(user=self.user, defaults={'bio': 'Initial bio'})

        self.client = Client()
        self.client.login(username='testuser', password='testpassword')

    def test_profile_not_found(self):
        self.profile.delete()

        response = self.client.get(reverse('profile_update'))

        self.assertRedirects(response, reverse('home'))
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Profile not found.')

    def test_profile_update_success(self):
        response = self.client.post(reverse('profile_update'), {
            'bio': 'Updated bio',
        })

        self.assertRedirects(response, reverse('home'))

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.bio, 'Updated bio')

        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Profile updated successfully.')


class DeleteProfileViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.profile, created = Profile.objects.get_or_create(user=self.user, defaults={'bio': 'Initial bio'})

        self.client = Client()
        self.client.login(username='testuser', password='testpassword')

    def test_delete_profile_not_found(self):
        self.profile.delete()

        response = self.client.delete(reverse('delete_profile'))

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"message": "Profile not found"})

    def test_delete_profile_success(self):
        response = self.client.delete(reverse('delete_profile'))

        self.assertEqual(response.status_code, 204)

        self.assertFalse(User.objects.filter(username='testuser').exists())
        self.assertFalse(Profile.objects.filter(user__username='testuser').exists())

    def test_delete_profile_invalid_method(self):
        response = self.client.get(reverse('delete_profile'))

        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json(), {"error": "Method not allowed"})


class SendFriendRequestViewTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password1')
        self.user2 = User.objects.create_user(username='user2', password='password2')
        self.profile1, created = Profile.objects.get_or_create(user=self.user1, defaults={'bio': 'Initial bio'})
        self.profile2, created = Profile.objects.get_or_create(user=self.user2, defaults={'bio': 'Initial bio'})

        self.client = Client()
        self.client.login(username='user1', password='password1')

    def test_profile_not_found(self):
        response = self.client.post(reverse('send_friend_request', args=[999]))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"message": "Profile not found"})

    def test_send_friend_request_to_self(self):
        response = self.client.post(reverse('send_friend_request', args=[self.profile1.id]))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"message": "You cannot add yourself as a friend"})

    def test_send_friend_request_success(self):
        response = self.client.post(reverse('send_friend_request', args=[self.profile2.id]))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {"message": "Friend request sent successfully"})

        friend_request = FriendRequest.objects.filter(from_user=self.user1, to_user=self.user2).first()
        self.assertIsNotNone(friend_request)

    def test_send_duplicate_friend_request(self):
        FriendRequest.objects.create(from_user=self.user1, to_user=self.user2)

        response = self.client.post(reverse('send_friend_request', args=[self.profile2.id]))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"message": "Friend request already sent"})

        friend_requests = FriendRequest.objects.filter(from_user=self.user1, to_user=self.user2)
        self.assertEqual(friend_requests.count(), 1)


class AcceptFriendRequestViewTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password1')
        self.user2 = User.objects.create_user(username='user2', password='password2')
        self.profile1, created = Profile.objects.get_or_create(user=self.user1, defaults={'bio': 'Initial bio'})
        self.profile2, created = Profile.objects.get_or_create(user=self.user2, defaults={'bio': 'Initial bio'})

        self.client = Client()
        self.client.login(username='user2', password='password2')

        self.friend_request = FriendRequest.objects.create(from_user=self.user1, to_user=self.user2)

    def test_accept_non_existent_friend_request(self):
        response = self.client.post(reverse('accept_friend_request', args=[999]))  # Invalid request ID
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {'error': 'Friend request does not exist'})

    def test_accept_friend_request_success(self):
        response = self.client.post(reverse('accept_friend_request', args=[self.friend_request.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'message': 'Friend request accepted successfully'})

        self.assertFalse(FriendRequest.objects.filter(pk=self.friend_request.id).exists())

        self.assertIn(self.profile2, self.profile1.friends.all())
        self.assertIn(self.profile1, self.profile2.friends.all())

    def test_accept_friend_request_mutual_friendship(self):
        response = self.client.post(reverse('accept_friend_request', args=[self.friend_request.id]))
        self.assertEqual(response.status_code, 200)

        self.profile1.refresh_from_db()
        self.profile2.refresh_from_db()
        self.assertIn(self.profile2, self.profile1.friends.all())
        self.assertIn(self.profile1, self.profile2.friends.all())


class FriendManagementViewTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password1')
        self.user2 = User.objects.create_user(username='user2', password='password2')
        self.user3 = User.objects.create_user(username='user3', password='password3')

        self.profile1, created = Profile.objects.get_or_create(user=self.user1, defaults={'bio': 'Initial bio'})
        self.profile2, created = Profile.objects.get_or_create(user=self.user2, defaults={'bio': 'Initial bio'})
        self.profile3, created = Profile.objects.get_or_create(user=self.user3, defaults={'bio': 'Initial bio'})

        self.client = Client()
        self.client.login(username='user1', password='password1')

        self.friend_request = FriendRequest.objects.create(from_user=self.user2, to_user=self.user1)

        self.profile1.friends.add(self.profile3)
        self.profile3.friends.add(self.profile1)

    def test_reject_nonexistent_friend_request(self):
        response = self.client.post(reverse('reject_friend_request', args=[999]))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"message": "Friend request not found"})

    def test_reject_friend_request_success(self):
        response = self.client.post(reverse('reject_friend_request', args=[self.friend_request.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Friend request rejected"})

        self.assertFalse(FriendRequest.objects.filter(pk=self.friend_request.id).exists())

    def test_remove_nonexistent_friend(self):
        response = self.client.delete(reverse('remove_friend', args=[self.profile2.id]))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"message": "You are not friends with this user"})

    def test_remove_friend_success(self):
        response = self.client.delete(reverse('remove_friend', args=[self.profile3.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Friend removed successfully"})

        self.assertNotIn(self.profile3, self.profile1.friends.all())
        self.assertNotIn(self.profile1, self.profile3.friends.all())

    def test_list_friends(self):
        response = self.client.get(reverse('list_friends'))
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')

        friends_list = soup.find('ul', {'id': 'friendsList'})
        self.assertIn(self.user3.username, friends_list.text)
        self.assertNotIn(self.user2.username, friends_list.text)

        pending_requests_section = soup.find('h4', text='Pending Friend Requests').find_next('ul')
        self.assertIn(self.user2.username, pending_requests_section.text)


class ProfileViewTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password1')

        if not Profile.objects.filter(user=self.user1).exists():
            self.profile1 = Profile.objects.create(user=self.user1)
        else:
            self.profile1 = Profile.objects.get(user=self.user1)

        self.client = Client()
        self.client.login(username='user1', password='password1')

    def test_profile_exists(self):
        response = self.client.get(reverse('profile_view', args=['user1']))
        self.assertEqual(response.status_code, 200)

    def test_profile_does_not_exist(self):
        response = self.client.get(reverse('profile_view', args=['nonexistentuser']))
        self.assertEqual(response.status_code, 404)


class PostManagementViewTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password1')
        self.user2 = User.objects.create_user(username='user2', password='password2')

        self.post1 = Post.objects.create(title='Post 1', content='Content 1', author=self.user1)
        self.post2 = Post.objects.create(title='Post 2', content='Content 2', author=self.user2)

        self.client = Client()
        self.client.login(username='user1', password='password1')

    def test_edit_post_success(self):
        response = self.client.post(reverse('edit_post', args=[self.post1.id]), {
            'title': 'Updated Title',
            'content': 'Updated Content',
        })
        self.assertRedirects(response, reverse('home'))

        self.post1.refresh_from_db()
        self.assertEqual(self.post1.title, 'Updated Title')
        self.assertEqual(self.post1.content, 'Updated Content')

    def test_edit_post_permission_denied(self):
        response = self.client.post(reverse('edit_post', args=[self.post2.id]), {
            'title': 'Attempted Title Change',
            'content': 'Attempted Content Change',
        })
        self.assertRedirects(response, reverse('home'))

        self.post2.refresh_from_db()
        self.assertNotEqual(self.post2.title, 'Attempted Title Change')
        self.assertNotEqual(self.post2.content, 'Attempted Content Change')

    def test_edit_post_invalid_form(self):
        response = self.client.post(reverse('edit_post', args=[self.post1.id]), {
            'title': '',
            'content': 'Updated Content',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required.')

        self.post1.refresh_from_db()
        self.assertNotEqual(self.post1.content, 'Updated Content')

    def test_delete_post_success(self):
        response = self.client.post(reverse('delete_post', args=[self.post1.id]))
        self.assertRedirects(response, reverse('home'))

        self.assertFalse(Post.objects.filter(id=self.post1.id).exists())

    def test_delete_post_permission_denied(self):
        response = self.client.post(reverse('delete_post', args=[self.post2.id]))
        self.assertRedirects(response, reverse('home'))

        self.assertTrue(Post.objects.filter(id=self.post2.id).exists())
