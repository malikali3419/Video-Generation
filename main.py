from VideoGeneration.videoGeneration import SpriteVideoGeneration
from dotenv import load_dotenv
import os


def main():
    global sprite_video_generator
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY", "")
    organization = os.getenv("ORGANIZATION_KEY", "")
    gemini_api_key = os.getenv("GEMINI_API_KEY", "")

    video_json = [
        {
            "video_prompt": "Create a sprite sheet of letter 'A' with 'A' for 'Apple' animation with 4 rows and 4 "
                            "columns",
            "duration": 100,
        },
        {
            "video_prompt": "Create a sprite sheet of letter 'B' with 'B' for 'Ball' animation with 4 rows and 4 "
                            "columns",
            "duration": 200,
        }
    ]
    videos_path = []
    for item in video_json:
        sprite_video_generator = SpriteVideoGeneration(
            api_key=api_key, organization=organization,
            gemini_api_key=gemini_api_key,
            default_size="1024x1024",
            default_quality="standard",
            max_tries=3
        )
        sprite_video_generator.generate_sprite_and_animation(
            prompt=item.get('video_prompt'),
            save_directory="generated_sprites",
            gemini_prompt="Please tell me how many rows and columns in this sprite sheet, tell me only rows and "
                          "columns no extra stuff please, answer me like that [rows] [columns].",
            animation_duration=item.get('duration'),
            animation_loop=0
        )
        videos_path.append(f"generated_sprites/{item.get('video_prompt')}/Extended_{item.get('video_prompt')}.mp4")
    sprite_video_generator.merge_and_resize_videos(video_paths=videos_path,
                                                   output_path="generated_sprites/final_output.mp4", target_width=480,
                                                   target_height=480)


if __name__ == "__main__":
    main()
