import os
import logging
from typing import Union, Tuple
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_audioclips
from moviepy.video.VideoClip import VideoClip
from moviepy.audio.AudioClip import AudioArrayClip

class VideoAudioMerger:
    def __init__(self, output_dir="output_videos"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    def merge(self, video_input: Union[str, VideoFileClip], audio_input: Union[str, AudioFileClip, Tuple], output_name: str = "merged_video.mp4", save: bool = False, fps: int = None) -> Union[str, VideoFileClip]:
        """
        Merges a video and an audio file.
        Auto-handles cases where one is longer than the other.
        Returns output file path or None if failed.
        """

        try:
            # --- Validate Inputs ---
            # --- Load Files ---
            video = video_input if isinstance(video_input, VideoClip) else VideoFileClip(video_input)

            if isinstance(audio_input, tuple):
                # (y, sr) numpy array pair
                y, sr = audio_input
                # AudioArrayClip expects shape (nframes, nchannels)
                if y.ndim == 1:
                    y2 = y.reshape((-1, 1))
                else:
                    y2 = y
                audio = AudioArrayClip(y2, fps=sr)
            elif isinstance(audio_input, AudioFileClip):
                audio = audio_input
            else:
                if not os.path.exists(audio_input):
                    raise FileNotFoundError(f"Audio file not found: {audio_input}")
                audio = AudioFileClip(audio_input)

            v_dur, a_dur = video.duration, audio.duration
            logging.info(f"Video length: {v_dur:.2f}s | Audio length: {a_dur:.2f}s")

            # --- Sync Durations ---
            if a_dur < v_dur:
                # Loop audio to match video length
                loop_count = int(v_dur // a_dur) + 1
                logging.info(f"Audio shorter → looping {loop_count}x to fit video.")
                audio_clips = [audio] * loop_count
                audio = concatenate_audioclips(audio_clips).subclip(0, v_dur)

            elif a_dur > v_dur:
                # Trim audio to match video
                logging.info("Audio longer → trimming to fit video duration.")
                audio = audio.subclip(0, v_dur)

            # --- Merge ---
            final_video = video.set_audio(audio)

            # --- Export or return clip ---
            output_path = os.path.join(self.output_dir, output_name)
            if save:
                write_kwargs = dict(codec="libx264", audio_codec="aac", threads=4, verbose=False, logger=None)
                if fps is not None:
                    write_kwargs['fps'] = fps
                final_video.write_videofile(output_path, **write_kwargs)

                # --- Cleanup ---
                video.close()
                try:
                    audio.close()
                except Exception:
                    pass
                final_video.close()

                logging.info(f"✅ Merged video created successfully: {output_path}")
                return output_path

            # Return the final in-memory clip (do not close it)
            return final_video

        except Exception as e:
            logging.error(f"❌ Merge failed: {e}")
            return None


# Example Usage:
if __name__ == "__main__":
    merger = VideoAudioMerger()
    result = merger.merge("video.mp4", "groovy-vibe-427121.mp3")
    print("Output video:", result)
