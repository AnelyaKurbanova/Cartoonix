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

class GenerateVideo(APIView):
    def post(self, request):
        user_prompt = request.data
        if not user_prompt:
            return JsonResponse({'error': 'No prompt provided'}, status=400)

        descriptions = generate_photo_descriptions(user_prompt)
        if not descriptions:
            return JsonResponse({'error': 'Failed to generate descriptions'}, status=500)

        image_urls = generate_images_from_descriptions(descriptions)
        if not image_urls:
            return JsonResponse({'error': 'Failed to generate images'}, status=500)

        s3_urls = []
        for image_url in image_urls:
            s3 = upload_image_to_s3(image_url)
            if s3:
                s3_urls.append(s3)

        if not s3_urls:
            return JsonResponse({'error': 'Failed to upload images to S3'}, status=500)

        video_b64s = generate_video_from_images_with_nvidia(s3_urls)
        if not video_b64s:
            return JsonResponse({'error': 'Failed to generate videos with Nvidia'}, status=500)

        s3_video_urls = []
        for video_b64 in video_b64s:
            video_data = base64.b64decode(video_b64)
            video_url = upload_video_to_s3(video_data)
            if video_url:
                s3_video_urls.append(video_url)

        video_prompt = VideoPrompt.objects.create(
            prompt=user_prompt,
            arrTitles=descriptions,
            arrImages=s3_urls,
            arrVideos=s3_video_urls
        )

        return JsonResponse({
            'message': 'Success',
            'video_prompt': {
                'id': video_prompt.id,
                'prompt': video_prompt.prompt,
                'arrTitles': video_prompt.arrTitles,
                'arrImages': video_prompt.arrImages,
                'arrVideos': video_prompt.arrVideos,
            }
        })

    
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