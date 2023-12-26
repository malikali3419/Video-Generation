import time

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
from utilities.senitizepath.senitizepath import SenitizePath


class SpriteVideoGeneration:
    """
    Class for generating videos using OpenAI DALL-E 3 and Geminai model.

    Attributes:
        client (OpenAI): OpenAI API client.
        default_size (str): Default size of the generated image.
        default_quality (str): Default quality of the generated image.

    Methods:
        download_image(prompt, url, save_directory): Downloads an image from the given URL and saves it in the specified directory.
        generate_and_download_sprite(prompt, save_directory, size=None, quality=None): Generates an image, downloads it, and saves it in the specified directory.
        get_image_url(prompt, size, quality): Generates an image URL using DALL-E 3.
    """

    def __init__(self, api_key: str, organization: str, gemini_api_key: str, default_size: str = "1024x1024",
                 default_quality: str = "standard", max_tries: int =1):

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

        self.output_mp4 = None
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
        self.max_tries = max_tries
        self.utils = SenitizePath()
        self.sprites = []

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
        for retry in range(self.max_tries):
            try:
                response = self.client.images.generate(
                    model="dall-e-3",
                    prompt=prompt,
                    size=size,
                    quality=quality,
                    n=1,
                )
                # Assuming 'data' and 'url' keys are available in the response
                image_url = response.data[0].url
                return image_url

            except Exception as e:
                print(f"Error generating image (attempt {retry + 1}/{3}): {e}")
                time.sleep(1)

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
        prompt = self.utils.senitize_path(prompt)
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

    def generate_and_download_sprite(self, prompt: str, save_directory: str, size: str = None,
                                     quality: str = None) -> str:

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

        prompt = self.utils.senitize_path(prompt)
        size = size or self.default_size
        quality = quality or self.default_quality
        image_url = self.get_image_url(prompt, size, quality)
        saved_image_path = self.download_image(
            prompt, image_url, save_directory)

        return saved_image_path

    def extract_sprites(self, row, col):

        """
        Extract sprites from the sprite sheet and store them in the sprites list.

        Args:
            rows (int): Number of rows in the sprite sheet.
            cols (int): Number of columns in the sprite sheet.
        """

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
        output_path = self.utils.senitize_path(output_path)
        self.sprites[0].save(
            output_path,
            save_all=True,
            append_images=self.sprites[1:],
            optimize=False,
            duration=duration,
            loop=loop
        )
    
    def get_sprite_details(self, gemini_prompt, image_path):
        """
        Generate Markdown content based on a prompt and an image with retries GEMINI.

        Parameters:
            - gemini_prompt (str): The Gemini prompt for content generation.
            - image_path (str): The path to the image used for content generation.

        Returns:
            tuple: Generated rows and columns.

        Raises:
            Exception: Raises the last encountered exception if max_attempts are exhausted.
        """
        for attempt in range(self.max_tries):
            try:
                image_path = self.utils.senitize_path(image_path)
                img = Image.open(image_path)
                response = self.model.generate_content([gemini_prompt, img], stream=True)
                response.resolve()
                numbers = re.findall(r'\d+', response.text)
                rows = int(numbers[0]) if numbers else 0
                columns = int(numbers[1]) if len(numbers) > 1 else 0
                print(rows, columns)
                return rows, columns
            except Exception as e:
                print(f"Attempt {attempt} failed. Error: {e}")
                if attempt == self.max_tries:
                    raise

    def loop_and_convert_into_mp4(self, input_gif, output_path):

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

            input_gif = self.utils.senitize_path(input_gif)
            output_path = self.utils.senitize_path(output_path)
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

    def generate_sprite_and_animation(self, prompt: str, save_directory: str, gemini_prompt: str,
                                      animation_duration: int = 150, animation_loop: int = 0):

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
        rows, cols = self.get_sprite_details(gemini_prompt, sprite_path)
        self.rows = rows
        self.cols = cols
        self.spritesheet_path = sprite_path
        self.create_animation(os.path.join(
            save_directory + "/" + prompt, f"{prompt}.gif"), duration=animation_duration, loop=animation_loop)
        self.loop_and_convert_into_mp4(os.path.join(
            save_directory + "/" + prompt, f"{prompt}.gif"),
            (save_directory + "/" + prompt + f"/Extended_{prompt}.mp4"))

    def merge_and_resize_videos(self, video_paths, output_path, target_width, target_height):
        clips = []
        for path in video_paths:
            path = self.utils.senitize_path(path=path)
            clip = VideoFileClip(path).resize(newsize=(target_width, target_height))
            clips.append(clip)

        final_clip = concatenate_videoclips(clips)
        final_clip.write_videofile(output_path)
