from django.urls import path
from ai.views import GenerateVideo

urlpatterns = [
    path('generate/', GenerateVideo.as_view()),
    path('generate/<int:pk>/', GenerateVideo.as_view()),
]
