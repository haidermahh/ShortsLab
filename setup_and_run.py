"""ShortsLab Automatic One-Click Setup & Launcher
Sets up virtual environment, dependencies, FFmpeg, speech model, frees port, opens browser, and runs the server.
"""
import os
import sys
import subprocess
import urllib.request
import zipfile
import time
import socket
import webbrowser
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV_DIR = ROOT / ".venv"
VENV_PYTHON = VENV_DIR / "Scripts" / "python.exe" if os.name == "nt" else VENV_DIR / "bin" / "python"
VENV_SCRIPTS = VENV_DIR / "Scripts" if os.name == "nt" else VENV_DIR / "bin"

def main():
    print("\n========================================================")
    print("                 ShortsLab Setup & Start                ")
    print("========================================================\n")

    # Step 1: Ensure venv
    if not VENV_PYTHON.exists():
        print("[1/4] Creating virtual environment (.venv)...")
        subprocess.check_call([sys.executable, "-m", "venv", str(VENV_DIR)])
    else:
        print("[1/4] Virtual environment (.venv) is ready.")

    # Add .venv/Scripts to PATH for this process and any child processes
    os.environ["PATH"] = str(VENV_SCRIPTS) + os.pathsep + os.environ.get("PATH", "")

    # Step 2: Ensure requirements installed
    flag_file = VENV_DIR / "installed.flag"
    if not flag_file.exists():
        print("[2/4] Installing Python dependencies (happens only on first run)...")
        subprocess.check_call([str(VENV_PYTHON), "-m", "pip", "install", "--upgrade", "pip"])
        subprocess.check_call([str(VENV_PYTHON), "-m", "pip", "install", "-r", str(ROOT / "requirements.txt")])
        flag_file.write_text("ok", encoding="utf-8")
    else:
        print("[2/4] Dependencies are installed.")

    # Step 3: Ensure FFmpeg
    ffmpeg_found = False
    for p in [str(VENV_SCRIPTS / "ffmpeg.exe"), "ffmpeg"]:
        try:
            subprocess.run([p, "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            ffmpeg_found = True
            break
        except Exception:
            pass

    if not ffmpeg_found:
        print("[3/4] Downloading FFmpeg for Windows (one-time setup, ~100 MB)...")
        ffmpeg_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
        zip_path = ROOT / "ffmpeg_temp.zip"
        urllib.request.urlretrieve(ffmpeg_url, zip_path)
        print("Extracting FFmpeg binaries...")
        with zipfile.ZipFile(zip_path, "r") as z:
            for f in z.filelist:
                if f.filename.endswith(("ffmpeg.exe", "ffprobe.exe")):
                    target = VENV_SCRIPTS / Path(f.filename).name
                    target.write_bytes(z.read(f))
        try:
            zip_path.unlink()
        except Exception:
            pass
        print("FFmpeg configured successfully!")
    else:
        print("[3/4] FFmpeg is ready.")

    # Step 4: Ensure speech recognition model
    tokens_file = ROOT / "data" / "models" / "sherpa-onnx-nemo-parakeet-tdt-0.6b-v2-int8" / "tokens.txt"
    if not tokens_file.exists():
        print("[4/4] Downloading speech recognition model (one-time setup, ~480 MB)...")
        subprocess.check_call([str(VENV_PYTHON), "-m", "studio.fetch_model"])
    else:
        print("[4/4] Speech model is ready.")

    # Step 5: Check and free port 8765 if busy (avoids Errno 10048)
    def free_port(port=8765):
        if os.name == "nt":
            for attempt in range(5):
                killed = False
                try:
                    out = subprocess.run(["netstat", "-ano", "-p", "tcp"], capture_output=True, text=True).stdout
                    for line in out.splitlines():
                        if f":{port}" in line and "LISTENING" in line:
                            parts = line.strip().split()
                            pid = parts[-1]
                            if pid.isdigit() and int(pid) != os.getpid():
                                print(f"Port {port} is currently in use (PID {pid}). Freeing port...")
                                subprocess.run(["taskkill", "/F", "/PID", pid], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                                killed = True
                except Exception:
                    pass
                if killed:
                    time.sleep(1.2)
                else:
                    break

    free_port(8765)

    # Step 6: Launch browser and server
    url = "http://127.0.0.1:8765"
    print("\n========================================================")
    print(f"  ShortsLab is starting at: {url}")
    print("  Opening your default browser...")
    print("========================================================\n")

    threading.Timer(2.0, lambda: webbrowser.open(url)).start()

    # Run the server
    try:
        subprocess.run([str(VENV_PYTHON), "-m", "studio.server"])
    except KeyboardInterrupt:
        print("\nShortsLab stopped.")

if __name__ == "__main__":
    main()
