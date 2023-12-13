from moviepy.editor import VideoFileClip, ImageClip, concatenate_videoclips

def loop_gif_to_mp4(input_gif, output_mp4, target_duration=20):
    # Read the original GIF
    original_clip = VideoFileClip(input_gif)

    # Get the duration of the original GIF
    original_duration = original_clip.duration

    # Calculate the number of times to repeat the original GIF
    num_repeats = int(target_duration / original_duration) + 1

    # Create a list to store VideoClip objects for the final video
    video_clips = []

    # Repeat the original GIF
    for _ in range(num_repeats):
        video_clips.append(original_clip)

    # Concatenate the VideoClip objects
    final_clip = concatenate_videoclips(video_clips)

    # Trim the final clip to the target duration
    final_clip = final_clip.subclip(0, target_duration)

    # Write the final video clip to an MP4 file
    final_clip.write_videofile(output_mp4, codec="libx264", audio_codec="aac")

if __name__ == "__main__":
    input_gif_path = "/Users/mac/Desktop/Loss_function/gif_videos_folder/letter_d_animation.gif"
    output_mp4_path = "output4.mp4"

    loop_gif_to_mp4(input_gif_path, output_mp4_path)
