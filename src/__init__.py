import os
from .audiosetting import AudioEnhancer
from .videosetting import VideoEnhancer
from .videomerger import VideoAudioMerger
from .conectintro import VideoMerger

class VideoProcessingApp:
    def __init__(self):
        self.audio_enhancer = AudioEnhancer()
        self.video_enhancer = VideoEnhancer()
        self.video_merger = VideoMerger()
        self.av_merger = VideoAudioMerger()

    # -------- Utility Functions --------
    def get_valid_path(self, prompt, expected_type):
        """Ask user for a valid path and confirm it’s correct."""
        while True:
            path = input(f"{prompt}: ").strip('"').strip()
            if not os.path.exists(path):
                print("❌ File not found! Try again.")
                continue

            # Type validation
            ext = os.path.splitext(path)[1].lower()
            if expected_type == "audio" and ext not in [".mp3", ".wav", ".m4a", ".flac"]:
                print("⚠️ That’s not an audio file! Please provide a valid audio format.")
                continue
            if expected_type == "video" and ext not in [".mp4", ".mov", ".avi", ".mkv"]:
                print("⚠️ That’s not a video file! Please provide a valid video format.")
                continue

            confirm = input(f"✅ Confirm file: {path} ? (y/n): ").strip().lower()
            if confirm == "y":
                return path

    # -------- Menu: Audio Enhancements --------
    def audio_menu(self):
        while True:
            print("\n🎧 AUDIO ENHANCEMENT MENU")
            print("1. Volume Up")
            print("2. Volume Down")
            print("3. Normalize")
            print("4. Fade In/Out")
            print("5. Speed Change")
            print("0. Go Back")

            choice = input("Select operation: ").strip()
            if choice == "0":
                break

            audio_path = self.get_valid_path("Enter audio file path", "audio")

            try:
                if choice == "1":
                    # increase volume by +5 dB
                    out = self.audio_enhancer.increase_volume(audio_path, db_gain=5.0, save=True)
                    print(f"✅ Saved: {out}")
                elif choice == "2":
                    # decrease volume by 5 dB (pass negative)
                    out = self.audio_enhancer.decrease_volume(audio_path, db_reduce=-5.0, save=True)
                    print(f"✅ Saved: {out}")
                elif choice == "3":
                    # normalize to target dB
                    out = self.audio_enhancer.normalize(audio_path, target_db=-14.0, save=True)
                    print(f"✅ Saved: {out}")
                elif choice == "4":
                    # apply fade in then fade out (write final file)
                    tmp = self.audio_enhancer.fade_in(audio_path, duration=2.0, save=False)
                    out = self.audio_enhancer.fade_out(tmp, duration=2.0, save=True)
                    print(f"✅ Saved: {out}")
                elif choice == "5":
                    speed = float(input("Enter speed factor (e.g., 1.5 for faster, 0.8 for slower): "))
                    out = self.audio_enhancer.speed_change(audio_path, factor=speed, save=True)
                    print(f"✅ Saved: {out}")
                else:
                    print("⚠️ Invalid choice.")
                    continue

                print("✅ Audio processed successfully.")
            except Exception as e:
                print(f"❌ Error: {e}")

    # -------- Menu: Video Enhancements --------
    def video_menu(self):
        while True:
            print("\n🎨 VIDEO ENHANCEMENT MENU")
            print("1. Adjust Color")
            print("2. Brightness/Contrast Only")
            print("0. Go Back")

            choice = input("Select operation: ").strip()
            if choice == "0":
                break

            video_path = self.get_valid_path("Enter video file path", "video")

            try:
                if choice == "1":
                    out = self.video_enhancer.adjust_color(video_path, brightness=0.1, contrast=1.2, saturation=1.3, save=True)
                    print(f"✅ Saved: {out}")
                elif choice == "2":
                    out = self.video_enhancer.adjust_color(video_path, brightness=0.2, contrast=1.5, save=True)
                    print(f"✅ Saved: {out}")
                else:
                    print("⚠️ Invalid choice.")
                    continue

                print("✅ Video processed successfully.")
            except Exception as e:
                print(f"❌ Error: {e}")

    # -------- Merge Two Videos --------
    def merge_videos(self):
        print("\n🎞️ MERGE TWO VIDEOS")
        video1 = self.get_valid_path("Enter first video path", "video")
        video2 = self.get_valid_path("Enter second video path", "video")

        try:
            result = self.video_merger.merge(video1, video2, save=True)
            print(f"✅ Videos merged successfully: {result}")
        except Exception as e:
            print(f"❌ Failed to merge: {e}")

    # -------- Merge Video + Audio --------
    def merge_audio_video(self):
        print("\n🎚️ MERGE VIDEO + AUDIO")
        video = self.get_valid_path("Enter video file path", "video")
        audio = self.get_valid_path("Enter audio file path", "audio")

        try:
            result = self.av_merger.merge(video, audio, output_name="merged_output.mp4", save=True)
            print(f"✅ Merged output saved: {result}")
        except Exception as e:
            print(f"❌ Failed: {e}")

    # -------- Full Pipeline --------
    def full_pipeline(self):
        print("\n🚀 FULL PIPELINE")
        video = self.get_valid_path("Enter video file path", "video")
        audio = self.get_valid_path("Enter audio file path", "audio")

        try:
            print("Step 1️⃣: Decreasing volume...")
            processed_audio = self.audio_enhancer.decrease_volume(audio, db_reduce=-10.0, save=False)

            print("Step 2️⃣: Enhancing video...")
            processed_video = self.video_enhancer.adjust_color(video, brightness=0.1, contrast=1.2, saturation=1.3, save=False)

            print("Step 3️⃣: Combining audio + video...")
            preferred_fps = getattr(processed_video, 'fps', 30)
            output = self.av_merger.merge(processed_video, processed_audio, output_name="final_output.mp4", save=True, fps=preferred_fps)

            print(f"✅ Final video ready: {output}")

        except Exception as e:
            print(f"❌ Pipeline failed: {e}")

    # -------- Main Menu --------
    def run(self):
        while True:
            print("\n=============================")
            print("🎬  VIDEO PROCESSING APP")
            print("=============================")
            print("1. Audio Enhancements")
            print("2. Video Enhancements")
            print("3. Merge Two Videos")
            print("4. Merge Video + Audio")
            print("5. Full Pipeline")
            print("0. Exit")
            print("=============================")

            choice = input("Select operation: ").strip()

            if choice == "1":
                self.audio_menu()
            elif choice == "2":
                self.video_menu()
            elif choice == "3":
                self.merge_videos()
            elif choice == "4":
                self.merge_audio_video()
            elif choice == "5":
                self.full_pipeline()
            elif choice == "0":
                print("👋 Goodbye!")
                break
            else:
                print("⚠️ Invalid choice. Try again.")


if __name__ == "__main__":
    app = VideoProcessingApp()
    app.run()
