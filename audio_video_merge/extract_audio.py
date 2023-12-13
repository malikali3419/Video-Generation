from moviepy.video.io.VideoFileClip import VideoFileClip

def extract_audio(video_path, audio_output_path):
    video_clip = VideoFileClip(video_path)
    audio_clip = video_clip.audio
    audio_clip.write_audiofile(audio_output_path)
    audio_clip.close()
    video_clip.close()

if __name__ == "__main__":
    video_file_path = "mp4_audios/JPM.mp4"  # Replace with the path to your video file
    audio_output_path = "audios/JPM.wav"  # Replace with the desired output audio file path

    extract_audio(video_file_path, audio_output_path)
