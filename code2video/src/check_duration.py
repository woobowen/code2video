import sys
import os
import subprocess
import imageio_ffmpeg

FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()
FFMPEG_DIR = os.path.dirname(FFMPEG_PATH)
if FFMPEG_DIR not in os.environ["PATH"]:
    os.environ["PATH"] = FFMPEG_DIR + os.pathsep + os.environ["PATH"]

def get_duration(filename):
    try:
        # Try using ffprobe if installed
        # ffprobe is usually in the same dir as ffmpeg
        ffprobe_path = os.path.join(FFMPEG_DIR, "ffprobe.exe") if os.name == 'nt' else os.path.join(FFMPEG_DIR, "ffprobe")
        if not os.path.exists(ffprobe_path):
             ffprobe_path = "ffprobe"

        result = subprocess.run(
            [ffprobe_path, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", filename],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode != 0:
            print(f"ffprobe error: {result.stderr}")
            return 0
        return float(result.stdout.strip())
    except Exception as e:
        print(f"Error checking duration: {e}")
        return 0

if __name__ == "__main__":
    file_path = r"CASES\User_Requested_BS_New_CLAUDE\0-Binary_Search\Binary_Search.mp4"
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        sys.exit(1)
        
    duration = get_duration(file_path)
    print(f"Duration: {duration} seconds")
    print(f"Duration: {duration/60} minutes")
