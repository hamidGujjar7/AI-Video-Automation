"""
audio_enhancer_librosa.py — Pure-Python, FFmpeg-free version

Dependencies:
  pip install librosa soundfile numpy

Features:
- Volume up/down
- Fade in/out
- Speed change (>2x & <0.5x)
- Reverse
- Normalize to target dB
- Cut (trim audio)
- Multi-step processing pipeline
"""

import os
import logging
import numpy as np
import librosa
import soundfile as sf
from typing import List, Tuple, Optional, Union


# ---------------- LOGGING ----------------
logger = logging.getLogger("AudioEnhancerLibrosa")
if not logger.handlers:
    h = logging.StreamHandler()
    h.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    logger.addHandler(h)
logger.setLevel(logging.INFO)


# ---------------- MAIN CLASS ----------------
class AudioEnhancer:
    """Pure-Python audio processor using librosa (no FFmpeg needed)."""

    def __init__(self, output_dir: str = "enhanced_audio"):
        self.output_dir = os.path.abspath(output_dir)
        os.makedirs(self.output_dir, exist_ok=True)

    # Utility for naming output files
    def _out(self, input_path: str, suffix: str) -> str:
        base = os.path.splitext(os.path.basename(input_path))[0]
        return os.path.join(self.output_dir, f"{base}_{suffix}.wav")

    def _load(self, path: str):
        y, sr = librosa.load(path, sr=None, mono=True)
        return y, sr

    def _save(self, y, sr, path: str):
        sf.write(path, y, sr)

    def _ensure_array(self, inp: Union[str, Tuple]) -> Tuple:
        """If inp is a filepath, load it. If it's a (y,sr) tuple, return as-is."""
        if isinstance(inp, tuple):
            return inp
        return self._load(inp)

    # ---------------- CORE OPS ----------------
    def increase_volume(self, input_path: Union[str, Tuple], db_gain: float = 3.0, save: bool = False) -> Optional[Union[Tuple, str]]:
        """Increase volume. If save=False (default) returns (y,sr). If save=True writes file and returns path."""
        y, sr = self._ensure_array(input_path)
        factor = 10 ** (db_gain / 20)
        y_out = np.clip(y * factor, -1.0, 1.0)
        if save:
            out = self._out(input_path if isinstance(input_path, str) else "audio", f"volup{db_gain}")
            self._save(y_out, sr, out)
            return out
        return y_out, sr

    def decrease_volume(self, input_path: Union[str, Tuple], db_reduce: float = -6.0, save: bool = False) -> Optional[Union[Tuple, str]]:
        y, sr = self._ensure_array(input_path)
        factor = 10 ** (db_reduce / 20)
        y_out = np.clip(y * factor, -1.0, 1.0)
        if save:
            out = self._out(input_path if isinstance(input_path, str) else "audio", f"voldown{abs(db_reduce)}")
            self._save(y_out, sr, out)
            return out
        return y_out, sr

    def fade_in(self, input_path: Union[str, Tuple], duration: float = 2.0, save: bool = False) -> Optional[Union[Tuple, str]]:
        y, sr = self._ensure_array(input_path)
        n = int(sr * duration)
        fade_curve = np.linspace(0.0, 1.0, n)
        y[:n] = y[:n] * fade_curve
        if save:
            out = self._out(input_path if isinstance(input_path, str) else "audio", f"fadein{duration}")
            self._save(y, sr, out)
            return out
        return y, sr

    def fade_out(self, input_path: Union[str, Tuple], duration: float = 2.0, save: bool = False) -> Optional[Union[Tuple, str]]:
        y, sr = self._ensure_array(input_path)
        n = int(sr * duration)
        fade_curve = np.linspace(1.0, 0.0, n)
        y[-n:] = y[-n:] * fade_curve
        if save:
            out = self._out(input_path if isinstance(input_path, str) else "audio", f"fadeout{duration}")
            self._save(y, sr, out)
            return out
        return y, sr

    def speed_change(self, input_path: Union[str, Tuple], factor: float = 1.25, save: bool = False) -> Optional[Union[Tuple, str]]:
        y, sr = self._ensure_array(input_path)
        y_fast = librosa.effects.time_stretch(y, rate=factor)
        if save:
            out = self._out(input_path if isinstance(input_path, str) else "audio", f"speed{factor}")
            self._save(y_fast, sr, out)
            return out
        return y_fast, sr

    def reverse(self, input_path: Union[str, Tuple], save: bool = False) -> Optional[Union[Tuple, str]]:
        y, sr = self._ensure_array(input_path)
        y_rev = y[::-1]
        if save:
            out = self._out(input_path if isinstance(input_path, str) else "audio", "reversed")
            self._save(y_rev, sr, out)
            return out
        return y_rev, sr

    def cut(self, input_path: Union[str, Tuple], start: float = 0.0, end: Optional[float] = None, save: bool = False) -> Optional[Union[Tuple, str]]:
        y, sr = self._ensure_array(input_path)
        start_idx = int(start * sr)
        end_idx = int(end * sr) if end else len(y)
        y_cut = y[start_idx:end_idx]
        if save:
            out = self._out(input_path if isinstance(input_path, str) else "audio", f"cut{start}-{end or 'end'}")
            self._save(y_cut, sr, out)
            return out
        return y_cut, sr

    def normalize(self, input_path: Union[str, Tuple], target_db: float = -1.0, save: bool = False) -> Optional[Union[Tuple, str]]:
        y, sr = self._ensure_array(input_path)
        rms = np.sqrt(np.mean(y ** 2))
        current_db = 20 * np.log10(rms + 1e-6)
        gain = target_db - current_db
        factor = 10 ** (gain / 20)
        y_norm = np.clip(y * factor, -1.0, 1.0)
        if save:
            out = self._out(input_path if isinstance(input_path, str) else "audio", f"norm{int(target_db)}dB")
            self._save(y_norm, sr, out)
            return out
        return y_norm, sr

    # ---------------- PIPELINE ----------------
    def apply_multiple(self, input_path: Union[str, Tuple], actions: List[Tuple[str, object]], save: bool = False) -> Optional[Union[Tuple, str]]:
        """
        Apply multiple actions in sequence. Each action is (method_name, arg) where arg may be None.
        If save=False (default) this returns an in-memory (y,sr) tuple. If save=True, writes final file and returns path.
        """
        temp = input_path
        intermediate_files = []
        try:
            for name, val in actions:
                fn = getattr(self, name, None)
                if not fn:
                    logger.error("Unknown action: %s", name)
                    return None
                logger.info("Applying: %s (%s)", name, val)
                if val is None:
                    res = fn(temp, save=False)
                else:
                    # If action is a numeric/primitive param, pass as keyword where appropriate
                    # Most methods accept (input, param, save=False)
                    res = fn(temp, val, save=False)
                if not res:
                    logger.error("Action failed: %s", name)
                    return None
                temp = res
            if save:
                # write final result
                y, sr = self._ensure_array(temp)
                out = self._out(input_path if isinstance(input_path, str) else "audio", "pipeline")
                self._save(y, sr, out)
                return out
            return temp
        finally:
            # no accidental deletes; intermediate files are not created unless user requested save True earlier
            pass


# ---------------- DEMO ----------------
if __name__ == "__main__":
    ae = AudioEnhancer()
    src = r"C:\Users\ASUS\OneDrive\Desktop\aivideoautomation\my_new_project\assist\groovy-vibe-427121.mp3"  # must be a .wav file

    if not os.path.exists(src):
        logger.error("⚠️ Missing input file: %s", src)
    else:
        final=ae.decrease_volume(src,db_reduce=-10.0)
       
        
        logger.info("✅ Final output: %s", final)
