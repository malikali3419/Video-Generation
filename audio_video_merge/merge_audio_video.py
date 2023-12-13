from moviepy.editor import VideoFileClip, AudioFileClip
import os
from pychorus import find_and_output_chorus
import uuid
from pydub import AudioSegment

def loop_chorus_segment(chorus_file_path:str,original_audio_path:str,loop_duration:int):
        audio_clip = None
        
        if os.path.exists(chorus_file_path):
            audio = AudioSegment.from_mp3(chorus_file_path)
        else:
            print(f"original audio path {original_audio_path}")
            audio = AudioSegment.from_mp3(original_audio_path)
        
        if len(audio)/1000.0>loop_duration:
            clipped_audio = audio[:loop_duration*1000]
            audio_clip = clipped_audio 
        else:
            looped_audio = audio
            loop_duration = int(loop_duration)
            for i in range(loop_duration):
                looped_audio +=audio 
            # Trim the audio to the exact duration if needed 
            looped_audio = looped_audio[:loop_duration*1000]
            audio_clip = looped_audio

        return audio_clip
def add_audio_to_video(video_path,audio_path,temp_dir="/Users/mac/Desktop/Loss_function/audio_video_merge_videos",new_video_dir= "/Users/mac/Desktop/Loss_function/audio_video_merge_videos"):
        video = VideoFileClip(video_path)

        # remove sound if sound already present in video        
        video = video.set_audio(None)

        # make dir if does not exist
        if not os.path.exists(temp_dir):
            os.mkdir(temp_dir)

        if not os.path.exists(new_video_dir):
            os.mkdir(new_video_dir)

        chorus_file_path = os.path.join(temp_dir,"temp.mp3")
        

        # will create a temp chorus file (.mp3)
        x = find_and_output_chorus(audio_path,chorus_file_path)
        
        loop_time = video.duration
        print(f"audio path {audio_path}")
        looped_audio = loop_chorus_segment(chorus_file_path,loop_duration=loop_time,original_audio_path=audio_path)

        looped_audio_path = os.path.join(temp_dir,"looped_audio.mp3")
        looped_audio.export(looped_audio_path,format='mp3')

        new_audio = AudioFileClip(looped_audio_path)
        video_with_audio = video.set_audio(new_audio)

        filename = str(uuid.uuid4()) + ".mp4"
        new_video_path = os.path.join(new_video_dir,filename)

        print("new video path = ",video_with_audio)

        video_with_audio.write_videofile(new_video_path)

        # delete temp file
        if os.path.exists(chorus_file_path): 
            os.remove(chorus_file_path)
        if os.path.exists(looped_audio_path):
            os.remove(looped_audio_path)
            
        os.rmdir(temp_dir)

        return new_video_path


add_audio_to_video("/Users/mac/Desktop/Loss_function/videos/4.mp4","audios/C.wav")