from django.urls import path
from ai.views import GenerateVideo, VideoDetail

urlpatterns = [
    path('generate/', GenerateVideo.as_view(), name='generate_video'),
    path('generate/<int:pk>/', VideoDetail.as_view(), name='video_detail'),
]

