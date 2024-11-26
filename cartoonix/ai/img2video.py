# import torch
# from diffusers import StableVideoDiffusionPipeline
# from diffusers.utils import load_image, export_to_video
# import os
# import time


# print("FlashAttention available:", torch.backends.cuda.flash_sdp_enabled())


# model_name = "stabilityai/stable-video-diffusion-img2vid-xt"

# # Загрузка модели
# pipe = StableVideoDiffusionPipeline.from_pretrained(
#     model_name, torch_dtype=torch.float16, variant="fp16"
# )
# # model = transformers.AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.bfloat16, attn_implementation="flash_attention_2").to('cuda')


# # Проверка наличия Triton и отключение оптимизаций, если требуется
# try:
#     pipe.unet = torch.compile(pipe.unet, mode="reduce-overhead", fullgraph=True)
#     pipe.unet.enable_forward_chunking()
#     # Перемещение модели на GPU
#     pipe.to("cuda")
# except Exception as e:
#     print(f"Error during optimization: {e}")
#     print("Proceeding without optimizations.")

# def generate_video_from_images(image_urls, output_folder='generated_videos'):
#     """
#     Generates video for each image in the list of URLs.

#     :param image_urls: List of image URLs
#     :param output_folder: Folder to save generated videos
#     :return: List of local paths to generated video files
#     """
#     if not os.path.exists(output_folder):
#         os.makedirs(output_folder)

#     video_paths = []
#     for idx, image_url in enumerate(image_urls):
#         try:
#             # Загрузка изображения
#             image = load_image(image_url)
#             image = image.resize((1024, 576))  # Ресайз изображения

#             # Генерация видео
#             generator = torch.manual_seed(42)  # Установка генератора
#             frames = pipe(image, decode_chunk_size=2, generator=generator, num_frames=25).frames[0]

#             # Сохранение видео
#             video_name = f"video_{int(time.time())}_{idx}.mp4"
#             video_path = os.path.join(output_folder, video_name)
#             export_to_video(frames, video_path, fps=7)
            
#             video_paths.append(video_path)
#         except Exception as e:
#             print(f"Error generating video for image {idx}: {e}")

#     return video_paths
