from openai import OpenAI
import requests
import os
from PIL import Image
import textwrap
import google.generativeai as genai
from moviepy.editor import VideoFileClip, concatenate_videoclips
import os
import re
import requests


class SpriteVideoGeneration:

    """
    Class for generating videos using OpenAI DALL-E 3 and Geminai modela.

    Attributes:
        client (OpenAI): OpenAI API client.
        default_size (str): Default size of the generated image.
        default_quality (str): Default quality of the generated image.

    Methods:
        download_image(prompt, url, save_directory): Downloads an image from the given URL and saves it in the specified directory.
        generate_and_download_sprite(prompt, save_directory, size=None, quality=None): Generates an image, downloads it, and saves it in the specified directory.
        get_image_url(prompt, size, quality): Generates an image URL using DALL-E 3.
    """


    def __init__(self, api_key: str, organization: str, gemini_api_key: str, default_size: str = "1024x1024", default_quality: str = "standard"):

        """
        Initialize the SpriteVideoGeneration.

        Args:
            api_key (str): OpenAI API key.
            organization (str): OpenAI organization ID.
            default_size (str): Default size of the generated image.
            default_quality (str): Default quality of the generated image.
            spritesheet_path (str): Path to the input sprite sheet image.
            rows (int): Number of rows in the sprite sheet.
            cols (int): Number of columns in the sprite sheet.
            sprite_width (int): Width of each sprite in the sprite sheet.
            sprite_height (int): Height of each sprite in the sprite sheet.
            sprites (list): List to hold each sprite image.
        """

        self.client = OpenAI(api_key=api_key, organization=organization)
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-pro-vision')
        self.default_size = default_size
        self.default_quality = default_quality
        self.spritesheet_path = ""
        self.rows = 0
        self.cols = 0
        self.sprite_width = 0
        self.sprite_height = 0
        self.target_duration = 20
        self.sprites = []

    def download_image(self, prompt: str, url: str, save_directory: str) -> str:

        """
        Downloads an image from the given URL and saves it in the specified directory.

        Args:
            prompt (str): A string that will be used to create nested folders.
            url (str): URL of the image to be downloaded.
            save_directory (str): Directory to save the downloaded image.

        Returns:
            str: File path of the saved image.
        """
        prompt = self.senitize_path(prompt)
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)

        prompt_folder = os.path.join(save_directory, prompt)
        if not os.path.exists(prompt_folder):
            os.makedirs(prompt_folder)

        image_name = os.path.join(prompt_folder, f"{prompt}.png")
        response = requests.get(url)

        if response.status_code == 200:
            with open(image_name, 'wb') as f:
                f.write(response.content)
            return image_name
        else:
            raise ValueError(
                f"Failed to download image from {url}. Status code: {response.status_code}")

    def generate_and_download_sprite(self, prompt: str, save_directory: str, size: str = None, quality: str = None) -> str:

        """
        Generates an image using DALL-E 3, downloads it, and saves it in the specified directory.

        Args:
            prompt (str): Prompt for DALL-E 3 image generation.
            save_directory (str): Directory to save the generated image.
            size (str): Size of the generated image (e.g., "1024x1024").
            quality (str): Quality of the generated image (e.g., "standard").

        Returns:
            str: File path of the saved image.
        """

        prompt = self.senitize_path(prompt)
        size = size or self.default_size
        quality = quality or self.default_quality
        image_url = self.get_image_url(prompt, size, quality)
        saved_image_path = self.download_image(
            prompt, image_url, save_directory)

        return saved_image_path

    def get_image_url(self, prompt: str, size: str, quality: str) -> str:

        """
        Generates an image URL using DALL-E 3.

        Args:
            prompt (str): Prompt for DALL-E 3 image generation.
            size (str): Size of the generated image (e.g., "1024x1024").
            quality (str): Quality of the generated image (e.g., "standard").

        Returns:
            str: Image URL.
        """

        response = self.client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size,
            quality=quality,
            n=1,
        )
        image_url = response.data[0].url
        return image_url

    def extract_sprites(self, row, col):
         
        """
        Extract sprites from the sprite sheet and store them in the sprites list.

        Args:
            rows (int): Number of rows in the sprite sheet.
            cols (int): Number of columns in the sprite sheet.
        """

        is_manual_input = input(
            "Do you want to enter the rows and columns manually (Y/N)? ")
        if is_manual_input.capitalize() == "Y":
            col = int(input("Enter the columns in sprite sheet : "))
            row = int(input("Enter the rows in sprite sheet: "))
        else:
            pass

        spritesheet = Image.open(self.spritesheet_path)
        self.sprite_width = spritesheet.width // col
        self.sprite_height = spritesheet.height // row

        for row in range(self.rows):
            for col in range(self.cols):
                left = col * self.sprite_width
                upper = row * self.sprite_height
                right = (col + 1) * self.sprite_width
                lower = (row + 1) * self.sprite_height

                sprite = spritesheet.crop((left, upper, right, lower))
                self.sprites.append(sprite)

    def create_animation(self, output_path: str, duration: int = 150, loop: int = 0):

        """
        Create a GIF animation from the sprite sheet and save it to the specified path.

        Args:
            output_path (str): Path to save the output GIF animation.
            duration (int): Duration for each frame in milliseconds.
            loop (int): Number of loops for the animation (use 0 for infinite loop).
        """
        
        if not self.sprites:
            self.extract_sprites(self.rows, self.cols)

        if not self.sprites:
            raise ValueError("No sprites found in the sprite sheet.")
        output_path = self.senitize_path(output_path)
        self.sprites[0].save(
            output_path,
            save_all=True,
            append_images=self.sprites[1:],
            optimize=False,
            duration=duration,
            loop=loop
        )

    def generate_markdown(self,gemini_path, image_path):

        """
        Generate Markdown content based on a prompt and an image.

        Parameters:
        - image_path (str): The path to the image used for content generation.

        Returns:
        str: Generated Markdown content ( rows and columns ).

        Raises:
        Any specific exceptions that might be raised during image processing or content generation.
        """
        image_path = self.senitize_path(image_path)
        img = Image.open(image_path)
        response = self.model.generate_content(
            ["Please tell me how many rows and columns in this sprite sheet, tell me only rows and columns no extra stuff please, answer me like that [rows] [columns].", img], stream=True)
        response.resolve()
        numbers = re.findall(r'\d+', response.text)

        rows = int(numbers[0]) if numbers else 0
        columns = int(numbers[1]) if len(numbers) > 1 else 0
        return rows, columns

    def convert(self, input_gif, output_path):

        """
        Convert a GIF file to an MP4 file with a specified target duration.

        Parameters:
        - input_gif (str): Path to the input GIF file.
        - output_path (str): Path to save the output MP4 file.

        Raises:
        - ValueError: If the input GIF file or output path is invalid.
        - IOError: If there is an issue reading or writing the video files.
        - Exception: For any other unexpected errors during the conversion process.
        """

        try:
            input_gif = self.senitize_path(input_gif)
            output_path = self.senitize_path(output_path)
            original_clip = VideoFileClip(input_gif)
            original_duration = original_clip.duration
            self.output_mp4 = output_path
            num_repeats = int(self.target_duration /
                             original_duration) + 1
            video_clips = []
            for _ in range(num_repeats):
                video_clips.append(original_clip)
            final_clip = concatenate_videoclips(video_clips)
            final_clip = final_clip.subclip(0, self.target_duration)
            final_clip.write_videofile(
                self.output_mp4, codec="libx264", audio_codec="aac")
        except Exception as e:
            print(f"Error: {e}")

    def generate_sprite_and_animation(self, prompt: str, save_directory: str, gemini_prompt: str, gemini_duration: int = 150, gemini_loop: int = 0):

        """
        Generate a sprite sheet, markdown content, animation, and video from prompts.

        Parameters:
        - prompt (str): The main prompt for generating the sprite sheet and animation.
        - save_directory (str): The directory to save generated files.
        - gemini_prompt (str): The prompt for generating markdown content.
        - gemini_duration (int, optional): Duration of the animation in seconds (default is 150).
        - gemini_loop (int, optional): Number of times to loop the animation (default is 0).

        Returns:
        str: The generated markdown content.

        Raises:
        - Any exceptions that might be raised by the underlying functions, such as file I/O errors or conversion errors.
        """

        sprite_path = self.generate_and_download_sprite(prompt, save_directory)
        rows, cols = self.generate_markdown(gemini_prompt, sprite_path)
        self.rows = rows
        self.cols = cols
        self.spritesheet_path = sprite_path
        self.create_animation(os.path.join(
            save_directory+"/"+prompt, f"{prompt}.gif"), duration=150, loop=gemini_loop)
        self.convert(os.path.join(
            save_directory+"/"+prompt, f"{prompt}.gif"), (save_directory+"/"+prompt + f"/Extended_{prompt}.mp4"))
        
    def merge_and_resize_videos(video_paths, output_path, target_width, target_height):
        clips = []
        for path in video_paths:
            path = self.senitize_path()
            clip = VideoFileClip(path).resize(newsize=(target_width, target_height))
            clips.append(clip)

        final_clip = concatenate_videoclips(clips)
        final_clip.write_videofile(output_path)

        
    def senitize_path(self, path):
        input_path = re.sub(r'[^\w\s./-]', '', path).strip()
        sanitized_input_gif = re.sub(r'[-\s]+', '_', input_path)
        return sanitized_input_gif
    
    def merge_and_resize_videos(self, video_paths, output_path, target_width, target_height):
        clips = []
        for path in video_paths:
            path = self.senitize_path(path=path)
            clip = VideoFileClip(path).resize(newsize=(target_width, target_height))
            clips.append(clip)

        final_clip = concatenate_videoclips(clips)
        final_clip.write_videofile(output_path)



def main():
    api_key = "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"
    organization = "org-rnPhpXwpaOziG9EogdrBxstV"
    gemini_api_key = "AIzaSyD5a0rAFcrr9ZnxyJBYXNz5s01Epta_R3A"

    video_json = {
        "prompt1": "Create a sprite sheet of letter 'E' with 'E' for 'Egg' animation with 4 rows and 4 columns",
        "prompt2": "Create a sprite sheet of letter 'F' with 'F' for 'Flag' animation with 4 rows and 4 columns",
    }
    videos_path = []
    for _, value in video_json.items():
        unified_generator = SpriteVideoGeneration(
            api_key, organization, gemini_api_key, "1024x1024", "standard")
        result = unified_generator.generate_sprite_and_animation(
            value, "generated_sprites", "Create animation", ("generated_sprites/"+value))
        videos_path.append(f"generated_sprites/{value}/Extended_{value}.mp4")
        print(result)
    unified_generator.merge_and_resize_videos(video_paths=videos_path,output_path="generated_sprites/final_output.mp4",target_width=128, target_height=128)

if __name__ == "__main__":
    main()

