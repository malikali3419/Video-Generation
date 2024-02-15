from moviepy.editor import VideoFileClip, concatenate_audioclips, AudioFileClip
from pychorus import find_and_output_chorus
from pydub import AudioSegment
import os
import uuid

def loop_audio_segment(audio_path, loop_duration):
    audio = AudioSegment.from_mp3(audio_path)
    audio_length_ms = len(audio)

    if audio_length_ms >= loop_duration * 1000:
        return audio[:loop_duration * 1000]

    repeat_times = int(loop_duration * 1000 // audio_length_ms)
    remaining_time = loop_duration * 1000 % audio_length_ms

    looped_audio = audio * repeat_times + audio[:remaining_time]
    return looped_audio

def add_audio_to_video(video_path, audio_paths):
    temp_dir = "/Users/mac/Desktop/Loss_function/audio_video_merge_videos"
    new_video_dir = "/Users/mac/Desktop/Loss_function/audio_video_merge_videos"
    video = VideoFileClip(video_path)

    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    if not os.path.exists(new_video_dir):
        os.makedirs(new_video_dir)
    total_duration = video.duration
    each_audio_duration = total_duration / len(audio_paths)

    looped_audios = []
    for audio_path in audio_paths:
        looped_audio = loop_audio_segment(audio_path, each_audio_duration)
        looped_audios.append(looped_audio)
    combined_audio = sum(looped_audios, AudioSegment.silent(duration=0))
    combined_audio_path = os.path.join(temp_dir, "combined_audio.wav")
    combined_audio.export(combined_audio_path, format='wav')
    new_audio = AudioFileClip(combined_audio_path)
    video_with_audio = video.set_audio(new_audio)
    filename = str(uuid.uuid4()) + ".mp4"
    new_video_path = os.path.join(new_video_dir, filename)
    video_with_audio.write_videofile(new_video_path)
    if os.path.exists(combined_audio_path):
        os.remove(combined_audio_path)
    return new_video_path

video_file = "final_output.mp4"
audio_files = ["audios/JPM.wav"]
new_video = add_audio_to_video(video_file, audio_files)
