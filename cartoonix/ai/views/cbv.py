from django.http import JsonResponse
from ai.models import VideoPrompt
from ai.gpt import generate_photo_descriptions, generate_images_from_descriptions
from ai.s3_utils import upload_image_to_s3, upload_video_to_s3
from ai.serializers import VideoPromptSerializer
from ai.nvidia import generate_video_from_images_with_nvidia
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status 
from django.shortcuts import render
import base64
import requests
from moviepy.editor import VideoFileClip, concatenate_videoclips
import uuid
import os
from rest_framework.renderers import JSONRenderer

class GenerateVideo(APIView):
    def post(self, request):
        try:
            # Получение prompt из данных запроса
            user_prompt = request.data.get("prompt")
            if not user_prompt:
                return Response({'error': 'No prompt provided'}, status=400)

            # Генерация описаний
            descriptions = generate_photo_descriptions(user_prompt)
            if not descriptions:
                return Response({'error': 'Failed to generate descriptions'}, status=500)

            # Генерация изображений
            image_urls = generate_images_from_descriptions(descriptions)
            if not image_urls:
                return Response({'error': 'Failed to generate images'}, status=500)

            # Загрузка изображений в S3
            s3_urls = [upload_image_to_s3(image) for image in image_urls if upload_image_to_s3(image)]

            if not s3_urls:
                return Response({'error': 'Failed to upload images to S3'}, status=500)

            # Генерация видео из изображений
            video_b64s = generate_video_from_images_with_nvidia(s3_urls)
            if not video_b64s:
                return Response({'error': 'Failed to generate videos with Nvidia'}, status=500)

            # Загрузка сгенерированных видео в S3
            s3_video_urls = []
            for video_b64 in video_b64s:
                video_data = base64.b64decode(video_b64)
                video_url = upload_video_to_s3(video_data)
                if video_url:
                    s3_video_urls.append(video_url)

            # Склейка видео
            def merge_videos(video_urls):
                output_file = f"{uuid.uuid4()}.mp4"
                clips = [VideoFileClip(url) for url in video_urls]
                final_clip = concatenate_videoclips(clips, method="compose")
                final_clip.write_videofile(output_file, codec="libx264", audio_codec="aac")
                for clip in clips:
                    clip.close()
                final_clip.close()
                return output_file

            merged_video = merge_videos(s3_video_urls)



            # Загрузка объединённого видео в S3
            with open(merged_video, "rb") as f:
                video_data = f.read()
            final_video_url = upload_video_to_s3(video_data)

            # Удаление локального файла
            os.remove(merged_video)

            # Создание записи в базе данных
            video_prompt = VideoPrompt.objects.create(
                prompt=user_prompt,
                arrTitles=descriptions,
                arrImages=s3_urls,
                arrVideos=s3_video_urls,
                finalVideo=final_video_url
            )

            serialized_data = VideoPromptSerializer(video_prompt).data

            return Response(serialized_data, status=201)

        except Exception as e:
            return Response({'error': str(e)}, status=500)
    
    def get(self, request):
        generatedVideos = VideoPrompt.objects.all()
        serializer = VideoPromptSerializer(generatedVideos, many=True)
        # return Response(serializer.data)
        return render(request, 'ai/video_list.html', {'videos': serializer.data})
    
class VideoDetail(APIView):
    def get_object(self, pk):
        try:
            video = VideoPrompt.objects.get(id=pk)
            return video
        except VideoPrompt.DoesNotExist as e:
            return Response({'error': str(e)})
        
    def get(self, request, pk):
        video = self.get_object(pk)
        serializer = VideoPromptSerializer(video)
        return Response(serializer.data)
    
    def put(self, request, pk):
        video = self.get_object(pk)
        serializer = VideoPromptSerializer(video, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
    def delete(self, request, pk=None):
        video = self.get_object(pk)
        video.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)