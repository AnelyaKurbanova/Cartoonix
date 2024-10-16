from django.http import JsonResponse
from ai.models import VideoPrompt
from ai.gpt import generate_photo_descriptions, generate_images_from_descriptions
from ai.s3_utils import upload_image_to_s3
from ai.serializers import VideoPromptSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status 

class GenerateVideo(APIView):
    def post(self, request):
        user_prompt = request.data
        if not user_prompt:
            return JsonResponse({'error': 'No prompt provided'}, status=400)

        descriptions = generate_photo_descriptions(user_prompt)

        if not descriptions:
            return JsonResponse({'error': 'Failed to generate descriptions'}, status=500)

        image_urls = generate_images_from_descriptions(descriptions)
        s3_urls = []
        for image_url in image_urls:
            s3 = upload_image_to_s3(image_url)
            if s3:
                s3_urls.append(s3)

        video_prompt = VideoPrompt.objects.create(
            prompt=user_prompt,
            arrTitles=descriptions,
            arrImages=s3_urls
        )

        return JsonResponse({
            'message': 'Success',
            'video_prompt': {
                'id': video_prompt.id,
                'prompt': video_prompt.prompt,
                'arrTitles': video_prompt.arrTitles,
                'arrImages': video_prompt.arrImages,
            }
        })
    
    def get(self, request):
        generatedVideos = VideoPrompt.objects.all()
        serializer = VideoPromptSerializer(generatedVideos, many=True)
        return Response(serializer.data)
    
class VideoDetail(APIView):
    def get_object(self, pk):
        try:
            video = VideoPrompt.objects.get(pk=pk)
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