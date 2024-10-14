from django.urls import path
from ai.views import GenerateVideoPromptView

urlpatterns = [
    path('generate/', GenerateVideoPromptView.as_view()),
]
