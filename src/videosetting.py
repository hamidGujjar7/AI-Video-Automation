"""
VideoEnhancerLite - FFmpeg-free MoviePy video processor
Runs on Windows/Mac/Linux without external setup.

Features:
- Brightness / Contrast / Saturation adjustment
- Speed change (>2x & <0.5x)
- Fade in/out
- Trim (cut)
- Add watermark (image or text)
- Add subtitles
- Extract audio
"""

import os
from typing import Optional, Union
from moviepy.editor import (
    VideoFileClip, CompositeVideoClip, vfx, TextClip, AudioFileClip
)
from moviepy.video.VideoClip import VideoClip
import numpy as np
from PIL import Image, ImageEnhance


class VideoEnhancer:
    """Pure Python + MoviePy video processor."""

    def __init__(self, output_dir: str = "enhanced_videos"):
        self.output_dir = os.path.abspath(output_dir)
        os.makedirs(self.output_dir, exist_ok=True)

    def _out(self, input_path: str, suffix: str, ext="mp4") -> str:
        base = os.path.splitext(os.path.basename(input_path))[0]
        return os.path.join(self.output_dir, f"{base}_{suffix}.{ext}")

    # ---------------- FILTERS ----------------
    def adjust_color(
        self,
        input_path: Union[str, VideoClip],
        brightness: float = 1.0,
        contrast: float = 1.0,
        saturation: float = 1.0,
        save: bool = False,
    ) -> Optional[Union[str, VideoFileClip]]:
        """Adjust brightness/contrast/saturation. Returns VideoFileClip when save=False, else writes file and returns path."""
        clip = input_path if isinstance(input_path, VideoClip) else VideoFileClip(input_path)

        def process_frame(frame):
            arr = np.asarray(frame)
            # Ensure we have uint8 RGB data for PIL
            if arr.dtype != np.uint8:
                # If values are in [0,1], scale up
                if arr.max() <= 1.0:
                    arr = (arr * 255).astype(np.uint8)
                else:
                    arr = arr.astype(np.uint8)
            img = Image.fromarray(arr)
            img = ImageEnhance.Brightness(img).enhance(brightness)
            img = ImageEnhance.Contrast(img).enhance(contrast)
            img = ImageEnhance.Color(img).enhance(saturation)
            return np.array(img)

        new_clip = clip.fl_image(process_frame)
        if save:
            output = self._out(input_path if isinstance(input_path, str) else getattr(input_path, 'filename', 'clip'), "color_adj")
            new_clip.write_videofile(output, codec="libx264", audio_codec="aac")
            clip.close()
            new_clip.close()
            return output
        # return clip object for in-memory pipeline
        # do not close source/new_clip here
        return new_clip

    def speed_change(self, input_path: Union[str, VideoClip], factor: float = 1.25, save: bool = False) -> Optional[Union[str, VideoClip]]:
        clip = input_path if isinstance(input_path, VideoClip) else VideoFileClip(input_path)
        new_clip = clip.fx(vfx.speedx, factor)
        if save:
            output = self._out(input_path if isinstance(input_path, str) else getattr(input_path, 'filename', 'clip'), f"speed{factor}")
            new_clip.write_videofile(output, codec="libx264", audio_codec="aac")
            clip.close()
            new_clip.close()
            return output
        return new_clip

    def fade_in_out(self, input_path: Union[str, VideoClip], fade_in: float = 1.0, fade_out: float = 1.0, save: bool = False) -> Optional[Union[str, VideoClip]]:
        clip = input_path if isinstance(input_path, VideoClip) else VideoFileClip(input_path)
        new_clip = clip.crossfadein(fade_in).crossfadeout(fade_out)
        if save:
            output = self._out(input_path if isinstance(input_path, str) else getattr(input_path, 'filename', 'clip'), "fade")
            new_clip.write_videofile(output, codec="libx264", audio_codec="aac")
            clip.close()
            new_clip.close()
            return output
        return new_clip

    def trim(self, input_path: Union[str, VideoClip], start: float = 0.0, end: Optional[float] = None, save: bool = False) -> Optional[Union[str, VideoClip]]:
        clip = input_path if isinstance(input_path, VideoClip) else VideoFileClip(input_path)
        new_clip = clip.subclip(start, end)
        if save:
            output = self._out(input_path if isinstance(input_path, str) else getattr(input_path, 'filename', 'clip'), f"cut{start}-{end or 'end'}")
            new_clip.write_videofile(output, codec="libx264", audio_codec="aac")
            clip.close()
            new_clip.close()
            return output
        return new_clip

    def add_watermark(self, input_path: Union[str, VideoClip], watermark_text: str = "Demo", pos=("right", "bottom"), save: bool = False) -> Optional[Union[str, VideoClip]]:
        clip = input_path if isinstance(input_path, VideoClip) else VideoFileClip(input_path)
        txt = (
            TextClip(watermark_text, fontsize=40, color="white", stroke_color="black")
            .set_duration(clip.duration)
            .set_pos(pos)
        )
        final = CompositeVideoClip([clip, txt])
        if save:
            output = self._out(input_path if isinstance(input_path, str) else getattr(input_path, 'filename', 'clip'), "wm")
            final.write_videofile(output, codec="libx264", audio_codec="aac")
            clip.close()
            final.close()
            return output
        return final

    def add_subtitles(self, input_path: Union[str, VideoClip], text: str, save: bool = False) -> Optional[Union[str, VideoClip]]:
        clip = input_path if isinstance(input_path, VideoClip) else VideoFileClip(input_path)
        txt = (
            TextClip(text, fontsize=35, color="white", bg_color="black", size=(clip.w, 80))
            .set_duration(clip.duration)
            .set_pos(("center", "bottom"))
        )
        final = CompositeVideoClip([clip, txt])
        if save:
            output = self._out(input_path if isinstance(input_path, str) else getattr(input_path, 'filename', 'clip'), "subtitled")
            final.write_videofile(output, codec="libx264", audio_codec="aac")
            clip.close()
            final.close()
            return output
        return final

    def extract_audio(self, input_path: Union[str, VideoClip], save: bool = False) -> Optional[Union[str, AudioFileClip]]:
        """Extract audio track. Returns MoviePy AudioFileClip when save=False, else writes mp3 and returns path."""
        clip = input_path if isinstance(input_path, VideoClip) else VideoFileClip(input_path)
        audio = clip.audio
        if save:
            output = self._out(input_path if isinstance(input_path, str) else getattr(input_path, 'filename', 'clip'), "audio", "mp3")
            audio.write_audiofile(output)
            clip.close()
            audio.close()
            return output
        return audio


# ---------------- DEMO ----------------
if __name__ == "__main__":
    ve = VideoEnhancer()
    src = "sample.mp4"

    if not os.path.exists(src):
        print(f"⚠ Missing video: {src}")
    else:
        print("🎬 Applying filters...")
        result = ve.adjust_color(src, brightness=1.2, contrast=1.1, saturation=1.3)
        print("✅ Done:", result)
