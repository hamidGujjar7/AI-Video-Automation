AI Video Automation — Quick Start

This project processes audio and video files and produces a final merged video. It ships with a simple interactive runner (`app.py`) so you don't need to write Python.

Quick steps (Windows / PowerShell):

1) (Optional) Activate the virtual environment if you created one:

```powershell
& C:/Users/ASUS/OneDrive/Desktop/aivideoautomation/.venv/Scripts/Activate.ps1
```

2) Run the interactive app from the project root:

```powershell
python .\my_new_project\app.py
```

3) Use the on-screen menu to:
- Enhance audio or video (in-memory by default)
- Merge intro + main videos or attach audio to a video
- Save the final output (the runner prints the saved path)

Run the smoke test (creates tiny test files and writes outputs):

```powershell
python .\my_new_project\tests\test.py
```

Where outputs appear:
- Final saved videos: `output_videos/`
- Merged videos: `merged_videos/`
- Intermediate/saved videos: `enhanced_videos/`
- Test outputs: `my_new_project/test_outputs/`

If `git add README.md` failed with "pathspec did not match any files", it simply means the file didn't exist yet. This README has now been created at:

`my_new_project/README.md`

To add and commit it now, from PowerShell run:

```powershell
cd C:\Users\ASUS\OneDrive\Desktop\aivideoautomation\my_new_project
git add README.md
git commit -m "Add README.md"
```

Notes:
- If dependencies are missing, install them with:
```powershell
pip install -r requirment.txt
```
- For text overlays, MoviePy may require ImageMagick on Windows. Ensure `magick` is in PATH.

If you'd like, I can:
- Create a one-line PowerShell helper to activate venv, install deps, and launch the app.
- Expand this into a longer `README.md` with screenshots and examples.



By hamidgujjar7