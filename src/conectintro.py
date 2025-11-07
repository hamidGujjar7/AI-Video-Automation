"""
VideoMergerLite - Safe, FFmpeg-free video joining using MoviePy

Features:
- Auto resize & codec normalization
- Optional crossfade transition
- No FFmpeg required (MoviePy handles backend)
- Clean, professional logging and reusable class
"""

import os
import logging
from typing import Optional, Union
from moviepy.editor import VideoFileClip, concatenate_videoclips
from moviepy.video.VideoClip import VideoClip
# ---- Pillow / MoviePy compatibility fix ----
from PIL import Image

# Pillow 10+ removed ANTIALIAS; MoviePy still expects it.
if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.Resampling.LANCZOS
# --------------------------------------------

from moviepy.editor import VideoFileClip, concatenate_videoclips
import logging

# ---------------- LOGGING ----------------
logger = logging.getLogger("VideoMergerLite")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)


# ---------------- MAIN CLASS ----------------
class VideoMerger:
    """Combine two videos (intro + main) with optional transition."""

    def __init__(self, output_dir: str = "merged_videos"):
        """
        Initialize VideoMergerLite and create output directory.
        """
        self.output_dir = os.path.abspath(output_dir)
        os.makedirs(self.output_dir, exist_ok=True)

    def _out(self, suffix: str = "merged") -> str:
        """
        Build safe output path for merged videos.
        """
        return os.path.join(self.output_dir, f"{suffix}.mp4")

    def _normalize(self, clip: VideoClip) -> VideoClip:
        """
        Normalize video resolution and fps for safe concatenation.
        Converts everything to 720p 30fps for consistency.
        """
        target_resolution = (1280, 720)
        return clip.resize(newsize=target_resolution).set_fps(30)

    def merge(self, intro_path: Union[str, VideoClip], main_path: Union[str, VideoClip], crossfade: float = 0.0, save: bool = False) -> Optional[Union[str, VideoClip]]:
        try:
            # If inputs are file paths, validate they exist. If they're clips, skip check.
            if isinstance(intro_path, str) and not os.path.exists(intro_path):
                logger.error("⚠️ Intro file is missing: %s", intro_path)
                return None
            if isinstance(main_path, str) and not os.path.exists(main_path):
                logger.error("⚠️ Main file is missing: %s", main_path)
                return None

            logger.info("🎬 Loading videos...")
            intro_clip = intro_path if isinstance(intro_path, VideoClip) else VideoFileClip(intro_path)
            main_clip = main_path if isinstance(main_path, VideoClip) else VideoFileClip(main_path)

            logger.info("📏 Normalizing videos to 720p / 30fps...")
            intro_clip = self._normalize(intro_clip)
            main_clip = self._normalize(main_clip)

            if crossfade > 0:
                logger.info("🎞️ Applying crossfade transition: %.1fs", crossfade)
                merged_clip = concatenate_videoclips(
                    [intro_clip.crossfadeout(crossfade), main_clip.crossfadein(crossfade)],
                    method="compose"
                )
            else:
                logger.info("🧩 Simple concatenation...")
                merged_clip = concatenate_videoclips([intro_clip, main_clip], method="compose")

            output = self._out("final_merged")
            logger.info("💾 Exporting merged video to %s", output)

            if save:
                merged_clip.write_videofile(
                    output,
                    codec="libx264",
                    audio_codec="aac",
                    threads=4,
                    temp_audiofile=os.path.join(self.output_dir, "temp_audio.m4a"),
                    remove_temp=True,
                    verbose=False,
                    logger=None
                )
                logger.info("✅ Merge complete: %s", output)
                # Close clips
                intro_clip.close()
                main_clip.close()
                merged_clip.close()
                return output

            # return the merged clip object for in-memory pipeline
            return merged_clip

        except Exception as e:
            logger.error("❌ Merge failed: %s", e)
            return None


# ---------------- DEMO ----------------
if __name__ == "__main__":

    vm = VideoMerger()

    path=r"C:\Users\ASUS\OneDrive\Desktop\aivideoautomation\my_new_project\assist\video.mp4"

    # Simple merge (returns a clip object unless save=True)
    final = vm.merge(path, path, save=False)

    # Or with crossfade transition
    # final = vm.merge(intro, main, crossfade=1.5)

    print("Output:", final)
