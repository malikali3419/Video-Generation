from openai import OpenAI
import requests
import os
from PIL import Image
import textwrap
import google.generativeai as genai
from moviepy.editor import VideoFileClip, concatenate_videoclips


class SpriteGenerator:
    def __init__(self, api_key: str, organization: str, default_size: str = "1024x1024", default_quality: str = "standard") -> None:
        self.client = OpenAI(api_key=api_key, organization=organization)
        self.default_size = default_size
        self.default_quality = default_quality

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
    

class SpriteSheetAnimator:
    """
    SpriteSheetAnimator class for creating GIF animations from sprite sheets.

    Attributes:
        spritesheet_path (str): Path to the input sprite sheet image.
        sprite_width (int): Width of each sprite in the sprite sheet.
        sprite_height (int): Height of each sprite in the sprite sheet.
        sprites (list): List to hold each sprite image.

    Methods:
        create_animation(output_path, duration, loop): Create a GIF animation from the sprite sheet.
    """
    def __init__(self, spritesheet_path: str, rows: int = 3, cols: int = 3):
        """
        Initialize the SpriteSheetAnimator.

        Args:
            spritesheet_path (str): Path to the input sprite sheet image.
            rows (int): Number of rows in the sprite sheet.
            cols (int): Number of columns in the sprite sheet.
        """
        self.spritesheet_path = spritesheet_path
        self.rows = rows
        self.cols = cols
        self.sprite_width = 0
        self.sprite_height = 0
        self.sprites = []

    def extract_sprites(self, row, col):
        """
        Extract sprites from the sprite sheet and store them in the sprites list.
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

    def create_animation(self, output_path: str, row: int, col: int, duration: int = 150, loop: int = 0):
        """
        Create a GIF animation from the sprite sheet and save it to the specified path.

        Args:
            output_path (str): Path to save the output GIF animation.
            duration (int): Duration for each frame in milliseconds.
            loop (int): Number of loops for the animation (use 0 for infinite loop).
        """
        if not self.sprites:
            self.extract_sprites(row, col)

        if not self.sprites:
            raise ValueError("No sprites found in the sprite sheet.")

        self.sprites[0].save(
            output_path,
            save_all=True,
            append_images=self.sprites[1:],
            optimize=False,
            duration=duration,
            loop=loop
        )

class MarkdownGenerator:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro-vision')

    @staticmethod
    def to_markdown(text):
        text = text.replace('•', '  *')
        return textwrap.indent(text, '> ', predicate=lambda _: True)

    def generate_markdown(self, prompt, image_path):
        img = Image.open(image_path)
        response = self.model.generate_content(["Please tell me how many rows and coloumns in this sprite sheet, tell me only rows and columns no extra stuff please, answer me like that [rows] [columns].", img], stream=True)
        response.resolve()
        return response.text


class LoopGifToMp4Converter:
    """
    Convert a GIF to an MP4 file by looping the original GIF to meet the target duration.

    Attributes:
        input_gif (str): Path to the input GIF file.
        output_mp4 (str): Path to save the output MP4 file.
        target_duration (int): Target duration for the final MP4 file in seconds.

    Methods:
        convert(): Perform the GIF to MP4 conversion and save the result.
    """

    def __init__(self, input_gif: str = "", output_mp4: str = "", target_duration: int = 20):
        """
        Initialize the LoopGifToMp4Converter.

        Args:
            input_gif (str): Path to the input GIF file.
            output_mp4 (str): Path to save the output MP4 file.
            target_duration (int): Target duration for the final MP4 file in seconds.
        """
        self.input_gif = input_gif
        self.output_mp4 = output_mp4
        self.target_duration = target_duration

    def convert(self, input_gif, output_path):
        """
        Convert the input GIF to an MP4 file with looping and save the result.
        """
        self.input_gif = input_gif
        self.output_mp4 = output_path
        original_clip = VideoFileClip(self.input_gif)
        original_duration = original_clip.duration
        num_repeats = int(self.target_duration / original_duration) + 1
        video_clips = []
        for _ in range(num_repeats):
            video_clips.append(original_clip)
        final_clip = concatenate_videoclips(video_clips)
        final_clip = final_clip.subclip(0, self.target_duration)
        final_clip.write_videofile(self.output_mp4, codec="libx264", audio_codec="aac")
        return final_clip


class ExtendedSpriteGenerator(SpriteGenerator, SpriteSheetAnimator, MarkdownGenerator, LoopGifToMp4Converter):
    def __init__(self, api_key: str, organization: str, gemini_api_key: str,sprite_sheet_path:str, default_size: str = "1024x1024", default_quality: str = "standard"):
        SpriteGenerator.__init__(self, api_key, organization, default_size, default_quality)
        SpriteSheetAnimator.__init__(self,sprite_sheet_path)
        MarkdownGenerator.__init__(self, gemini_api_key)
        LoopGifToMp4Converter.__init__(self)

    def generate_sprite_and_animation(self, prompt: str, save_directory: str, gemini_prompt: str, gemini_output_path: str, gemini_duration: int = 150, gemini_loop: int = 0):
        # Generate and download sprite
        sprite_path = self.generate_and_download_sprite(prompt, save_directory)

        # Create animation
        gemini_markdown = self.generate_markdown(gemini_prompt, sprite_path)
        row = int(gemini_markdown[2])
        col = int(gemini_markdown[6])
        self.spritesheet_path = sprite_path
        self.create_animation(os.path.join(save_directory+"/"+prompt, f"{prompt}.gif"), row=row, col=col, duration=gemini_duration, loop=gemini_loop)
        self.convert(os.path.join(save_directory+"/"+prompt, f"{prompt}.gif"),(save_directory+"/"+prompt))

        # Generate markdown


        return gemini_markdown

if __name__ == "__main__":
    api_key = "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"
    organization = "org-rnPhpXwpaOziG9EogdrBxstV"
    gemini_api_key = "AIzaSyD5a0rAFcrr9ZnxyJBYXNz5s01Epta_R3A"
    # sprite_generator = SpriteGenerator(
    #     api_key="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", organization="org-rnPhpXwpaOziG9EogdrBxstV")
    video_json = {
        "prompt1": "Create a sprite sheet of lettter 'C' with 'C' for 'Cat' animation with 4 rows and 4 columns",
        "prompt2": "Create a sprite sheet of lettter 'D' with 'D' for 'Dog' animation with 4 rows and 4 columns",
    }
    for key, value in video_json.items():
        extended_generator = ExtendedSpriteGenerator(api_key, organization, gemini_api_key,"generated_sprites")
        result = extended_generator.generate_sprite_and_animation(value, "generated_sprites", "Create animation",("generated_sprites/"+value))
        print(result)

