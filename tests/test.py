import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

from audiosetting import AudioEnhancer
from videosetting import VideoEnhancer
from conectintro import VideoMerger
from videomerger import VideoAudioMerger
import numpy as np
from moviepy.editor import ColorClip


def run_smoke_test():
    root = Path(__file__).resolve().parents[1]
    out_dir = root / 'test_outputs'
    (out_dir).mkdir(parents=True, exist_ok=True)

    # tiny audio (1s sine)
    sr = 22050
    t = np.linspace(0, 1.0, int(sr * 1.0), endpoint=False)
    y = (0.1 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)

    A = AudioEnhancer(output_dir=str(out_dir / 'audio'))
    V = VideoEnhancer(output_dir=str(out_dir / 'video'))
    VM = VideoMerger(output_dir=str(out_dir / 'merged_videos'))
    VAM = VideoAudioMerger(output_dir=str(out_dir / 'final_videos'))

    results = {}

    print('OUT_DIR:', out_dir)

    print('1) Audio in-memory...')
    a_y_sr = A.decrease_volume((y, sr), db_reduce=-6.0, save=False)
    results['audio_inmem'] = isinstance(a_y_sr, tuple) and len(a_y_sr) == 2

    print('2) Audio save to file...')
    a_path = A.decrease_volume((y, sr), db_reduce=-6.0, save=True)
    results['audio_saved_exists'] = Path(a_path).exists()

    print('3) Video in-memory...')
    clip = ColorClip(size=(320, 240), color=(255, 0, 0), duration=1).set_fps(24)
    new_clip = V.adjust_color(clip, brightness=1.05, contrast=1.02, saturation=1.0, save=False)
    results['video_inmem'] = hasattr(new_clip, 'duration')

    print('4) Video save to file...')
    video_path = V.adjust_color(clip, brightness=1.05, contrast=1.02, saturation=1.0, save=True)
    results['video_saved_exists'] = Path(video_path).exists()

    print('5) Merge videos in-memory...')
    merged_clip = VM.merge(clip, new_clip, save=False)
    results['merge_inmem'] = hasattr(merged_clip, 'duration')

    print('6) Merge videos save...')
    merged_path = VM.merge(clip, new_clip, save=True)
    results['merge_saved_exists'] = Path(merged_path).exists()

    print('7) Attach audio in-memory...')
    final_clip = VAM.merge(new_clip, (y, sr), save=False)
    results['va_inmem'] = hasattr(final_clip, 'duration')

    print('8) Final save...')
    final_path = VAM.merge(new_clip, (y, sr), output_name='smoke_test_output.mp4', save=True, fps=24)
    results['va_saved_exists'] = Path(final_path).exists()

    print('\nSMOKE TEST RESULTS:')
    ok = True
    for k, v in results.items():
        print(f"- {k}: {v}")
        if not v:
            ok = False

    # cleanup: close clips
    try:
        clip.close()
        new_clip.close()
        merged_clip.close()
        final_clip.close()
    except Exception:
        pass

    return ok, results


if __name__ == '__main__':
    ok, results = run_smoke_test()
    if not ok:
        print('\nSome checks failed — see results above')
        sys.exit(2)
    print('\nAll smoke tests passed.')
    sys.exit(0)
