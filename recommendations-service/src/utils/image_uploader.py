import base64
import io
import os
import dotenv
import json
from pathlib import Path
from PIL import Image
from openai import OpenAI
from pydantic import BaseModel

rec_dir = Path(__file__).parent.parent.parent
env_file = rec_dir / "secret/openai.env"
dotenv.load_dotenv(env_file)

API_KEY: str = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY not found in environment variables.")

client = OpenAI(api_key=API_KEY)


def resize_image(image, max_dimension):
    if image.mode == "P":
        image = image.convert("RGBA" if "transparency" in image.info else "RGB")

    width, height = image.size
    if width > max_dimension or height > max_dimension:
        if width > height:
            new_width, new_height = max_dimension, int(height * (max_dimension / width))
        else:
            new_width, new_height = int(width * (max_dimension / height)), max_dimension
        image = image.resize((new_width, new_height), Image.LANCZOS)
    return image


def convert_to_png(image):
    with io.BytesIO() as output:
        image.save(output, format="PNG")
        return output.getvalue()


def process_image(path, max_size):
    with Image.open(path) as image:
        if image.format == "PNG" and max(image.size) <= max_size:
            with open(path, "rb") as f:
                encoded_image = base64.b64encode(f.read()).decode('utf-8')
        else:
            resized_image = resize_image(image, max_size)
            png_image = convert_to_png(resized_image)
            encoded_image = base64.b64encode(png_image).decode('utf-8')
        return encoded_image


class ImageAnalysis(BaseModel):
    tags: list[str]
    title: str


def generate_tags_and_title(image_path: str | Path):
    user_msg = "Analyze this image and provide descriptive tags and a name for it."
    system_msg = """
    You are an AI assistant specialized in analyzing images and generating descriptive metadata. 
    Your task is to:
    1. Analyze the image and generate tags that describe:
       - The main subject or objects in the image.
       - The emotional tone or mood of the image (e.g., happy, sad, peaceful, dramatic).
       - The attributes of the image (e.g., color palette, style, lighting).
       - Any other elements that help characterize the image accurately.
    2. Generate between 4 and 20 descriptive tags. Tags must:
       - Contain only Latin letters or numbers.
       - Be single words without spaces or special characters.
       - Tags can be compound words using the following formats:
         * PascalCase (e.g., RainReflection)
         * kebab-case (e.g., rain-reflection)
         * snake_case (e.g., rain_reflection)
    3. Create a title for the image that is slightly abstract, capturing not only its content but also its mood or atmosphere.
    
    Respond strictly in JSON format:
    {
      "tags": ["tag1", "tag2", "tag3", ...],
      "title": "picture title"
    }
    DO NOT WRITE ANYTHING SUPERFLUOUS, NO UNNECESSARY SYMBOLS OR EXPLANATIONS. 
    """

    encoded_image = process_image(image_path, max_size=512)
    file_name = os.path.basename(image_path)
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_msg},
            {
                "role": "user",
                "content": [
                    {"type": "text",
                     "text": f"{user_msg}\n\n---\n\nUploaded image:\n{os.path.basename(image_path)}"},
                    {"type": "image_url",
                     "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}}
                ]
            },
        ],
        n=1,
        temperature=0.3,
        response_format=ImageAnalysis
    )
    result = completion
    return result.choices[0].message.parsed


images_dir = rec_dir / "pixiv_images"
save_output_path = rec_dir / "data.json"
counter = 0
for img_name in os.listdir(images_dir):
    counter += 1
    with open(save_output_path, "r") as file:
        data = json.load(file)

    processed_image_names = [i["image_name"] for i in data]
    if img_name in processed_image_names:
        print(f"image {img_name} is already processed, continue this image")
        continue
    print(f"Processing img_name: {img_name} ... \t\t Counter={counter}")

    image_path = images_dir / img_name
    result: ImageAnalysis = generate_tags_and_title(image_path=image_path)

    image_data = {
        "image_name": img_name,
        "tags": result.tags,
        "title": result.title,
    }
    data.append(image_data)

    with open(save_output_path, "w") as file:
        json.dump(data, file, indent=4)
