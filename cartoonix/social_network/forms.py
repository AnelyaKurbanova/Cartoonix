from django.contrib.auth.models import User
from django import forms

from django.contrib.auth.forms import UserCreationForm
from .models import Post, Comment, Like, Profile

from .models import Post
from ai.models import VideoPrompt


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio']