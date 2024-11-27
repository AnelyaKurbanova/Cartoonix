import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

system_prompt = """
You are a creative screenwriter and a skilled visual storyteller. Your task is to generate a sequence of five photo descriptions based on a short user prompt, which together form a coherent narrative for a video. Each description should be vivid, detailed, and clearly convey the scenes, establishing logical connections between them.

1. Input: Receive a brief user request describing what kind of video they want to create.

2. Task: Based on this request, generate five short, connected descriptions of photos that can form the storyline of a video.

3. Description format:
   - Each description should be a separate scene (photo).
   - Describe important details: the setting, characters, emotions, actions, atmosphere, and color scheme.
   - Ensure that all the descriptions are logically and narratively connected.

4. Output: Always return exactly five descriptions in list format, connected by a coherent storyline.

5. Example Output:
   1. A misty forest at dawn, with rays of sunlight piercing through fog and illuminating ancient, towering trees; a sense of mystery and serenity prevails.
   2. A close-up of a shimmering dewdrop on a vibrant green leaf, reflecting a tiny hidden woodland creature peeking out with curiosity.
   3. An enchanting clearing with colorful flowers and a gentle stream; magical creatures gather, sharing whispers and songs.
   4. A mystical cave entrance covered in ivy, with soft glowing lights suggesting a hidden world within.
   5. A whimsical scene of sunset over the forest, creatures bidding farewell, as stars begin to twinkle in the darkening sky.

6. Language requirement: Regardless of the language of the user’s request, all photo descriptions must be strictly in English.
"""


def generate_photo_descriptions(user_prompt):
    """
    Generate five photo descriptions for a video storyline based on the user's request.

    :param user_prompt: User's text request
    :return: Array of five photo descriptions
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Create a video prompt for the following: {user_prompt}"}
            ]
        )
        
        photo_descriptions_text = response.choices[0].message.content
        
        lines = photo_descriptions_text.split('\n')
        
        photo_descriptions = []
        for line in lines:
            stripped_line = line.strip()
            if stripped_line and stripped_line[0].isdigit() and stripped_line[1] == '.':
                photo_descriptions.append(stripped_line)
        
        if len(photo_descriptions) != 5:
            raise ValueError("Unexpected number of descriptions received")
        
        print(f"Generated photo descriptions: {photo_descriptions}")
        return photo_descriptions
    except Exception as e:
        print(f"Error generating photo descriptions: {e}")
        return ['Error generating description'] * 5


def generate_images_from_descriptions(descriptions):
    """
    Generate images using DALL·E based on a list of descriptions.

    :param descriptions: List of text descriptions
    :return: List of URLs of generated images
    """
    image_urls = []
    try:
        for description in descriptions:
            response = client.images.generate(
                model="dall-e-3",
                prompt=description,
                size="1024x1024",
                quality="standard",
                n=1
            )
            image_url = response.data[0].url
            image_urls.append(image_url)
            print(f"Generated image URL: {image_url}")
        return image_urls
    except Exception as e:
        print(f"Error generating images: {e}")
        return []

