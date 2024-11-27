import logging
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
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
from moviepy import VideoFileClip, concatenate_videoclips
import uuid
import os

logger = logging.getLogger('api_logger')


class GenerateVideo(APIView):
    @swagger_auto_schema(
        operation_summary="Generate video from user prompt",
        operation_description="This endpoint generates a video based on the given user prompt.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'prompt': openapi.Schema(type=openapi.TYPE_STRING, description="User's prompt to generate the video")
            },
            required=['prompt']
        ),
        responses={
            201: VideoPromptSerializer,
            400: "Bad Request: Prompt is missing or invalid",
            500: "Internal Server Error"
        }
    )
    def post(self, request):
        logger.info("POST request to GenerateVideo endpoint.")
        try:
            user_prompt = request.data.get("prompt")
            if not user_prompt:
                logger.warning("No prompt provided in request.")
                return Response({'error': 'No prompt provided'}, status=400)

            logger.info(f"Generating video for prompt: {user_prompt}")

            descriptions = generate_photo_descriptions(user_prompt)
            if not descriptions:
                logger.error("Failed to generate descriptions.")
                return Response({'error': 'Failed to generate descriptions'}, status=500)

            image_urls = generate_images_from_descriptions(descriptions)
            if not image_urls:
                logger.error("Failed to generate images.")
                return Response({'error': 'Failed to generate images'}, status=500)

            s3_urls = [upload_image_to_s3(image) for image in image_urls if upload_image_to_s3(image)]
            if not s3_urls:
                logger.error("Failed to upload images to S3.")
                return Response({'error': 'Failed to upload images to S3'}, status=500)

            logger.info(f"Uploaded images to S3: {s3_urls}")

            video_b64s = generate_video_from_images_with_nvidia(s3_urls)
            if not video_b64s:
                logger.error("Failed to generate videos with Nvidia.")
                return Response({'error': 'Failed to generate videos with Nvidia'}, status=500)

            s3_video_urls = []
            for video_b64 in video_b64s:
                video_data = base64.b64decode(video_b64)
                video_url = upload_video_to_s3(video_data)
                if video_url:
                    s3_video_urls.append(video_url)

            logger.info(f"Uploaded videos to S3: {s3_video_urls}")

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

            with open(merged_video, "rb") as f:
                video_data = f.read()
            final_video_url = upload_video_to_s3(video_data)

            os.remove(merged_video)
            logger.info(f"Final video uploaded to S3: {final_video_url}")

            video_prompt = VideoPrompt.objects.create(
                prompt=user_prompt,
                arrTitles=descriptions,
                arrImages=s3_urls,
                arrVideos=s3_video_urls,
                finalVideo=final_video_url
            )

            serialized_data = VideoPromptSerializer(video_prompt).data
            logger.info("VideoPrompt successfully created and saved to database.")
            return Response(serialized_data, status=201)

        except Exception as e:
            logger.error(f"Error during video generation: {str(e)}")
            return Response({'error': str(e)}, status=500)

    @swagger_auto_schema(
        operation_summary="Retrieve all generated videos",
        operation_description="Returns a list of all video prompts with their associated data.",
        responses={
            200: VideoPromptSerializer(many=True),
        }
    )
    def get(self, request):
        logger.info("GET request to GenerateVideo endpoint.")
        generatedVideos = VideoPrompt.objects.all()
        serializer = VideoPromptSerializer(generatedVideos, many=True)
        return render(request, 'ai/video_list.html', {'videos': serializer.data})


class VideoDetail(APIView):
    @swagger_auto_schema(
        operation_summary="Retrieve a single video by ID",
        responses={
            200: VideoPromptSerializer,
            404: "Not Found"
        }
    )
    def get(self, request, pk):
        logger.info(f"GET request to VideoDetail for ID {pk}.")
        try:
            video = VideoPrompt.objects.get(id=pk)
            serializer = VideoPromptSerializer(video)
            return Response(serializer.data)
        except VideoPrompt.DoesNotExist:
            logger.warning(f"Video with ID {pk} not found.")
            return Response({'error': 'Video not found'}, status=404)

    @swagger_auto_schema(
        operation_summary="Update a video by ID",
        request_body=VideoPromptSerializer,
        responses={
            200: VideoPromptSerializer,
            400: "Bad Request",
            404: "Not Found"
        }
    )
    def put(self, request, pk):
        logger.info(f"PUT request to update VideoPrompt with ID {pk}.")
        try:
            video = VideoPrompt.objects.get(id=pk)
            serializer = VideoPromptSerializer(video, data=request.data)
            if serializer.is_valid():
                serializer.save()
                logger.info(f"VideoPrompt with ID {pk} updated successfully.")
                return Response(serializer.data)
            logger.warning(f"Validation failed for VideoPrompt update: {serializer.errors}")
            return Response(serializer.errors, status=400)
        except VideoPrompt.DoesNotExist:
            logger.warning(f"Video with ID {pk} not found.")
            return Response({'error': 'Video not found'}, status=404)

    @swagger_auto_schema(
        operation_summary="Delete a video by ID",
        responses={
            204: "No Content",
            404: "Not Found"
        }
    )
    def delete(self, request, pk=None):
        logger.info(f"DELETE request to remove VideoPrompt with ID {pk}.")
        try:
            video = VideoPrompt.objects.get(id=pk)
            video.delete()
            logger.info(f"VideoPrompt with ID {pk} deleted successfully.")
            return Response(status=status.HTTP_204_NO_CONTENT)
        except VideoPrompt.DoesNotExist:
            logger.warning(f"Video with ID {pk} not found.")
            return Response({'error': 'Video not found'}, status=404)
