import logging
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Post, Comment, Profile

logger = logging.getLogger('form_logger')


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'image']

    def clean(self):
        cleaned_data = super().clean()
        if 'title' in cleaned_data and len(cleaned_data['title']) < 5:
            logger.warning(f"PostForm validation failed: Title too short ('{cleaned_data['title']}').")
            raise forms.ValidationError("Title must be at least 5 characters long.")
        logger.info(f"PostForm validated successfully for post title: '{cleaned_data.get('title')}'.")
        return cleaned_data


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

    def clean(self):
        cleaned_data = super().clean()
        if 'content' in cleaned_data and len(cleaned_data['content']) < 3:
            logger.warning(f"CommentForm validation failed: Content too short ('{cleaned_data['content']}').")
            raise forms.ValidationError("Comment must be at least 3 characters long.")
        logger.info(f"CommentForm validated successfully for comment content: '{cleaned_data.get('content')}'.")
        return cleaned_data


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            logger.warning(f"UserRegisterForm validation failed: Email '{email}' already in use.")
            raise forms.ValidationError("Email is already in use.")
        logger.info(f"UserRegisterForm validated successfully for email: '{email}'.")
        return email


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio']

    def clean(self):
        cleaned_data = super().clean()
        bio = cleaned_data.get('bio')
        if bio and len(bio) > 500:
            logger.warning(f"ProfileUpdateForm validation failed: Bio too long ('{len(bio)}' characters).")
            raise forms.ValidationError("Bio must be 500 characters or less.")
        logger.info(f"ProfileUpdateForm validated successfully for bio: '{bio}'.")
        return cleaned_data
