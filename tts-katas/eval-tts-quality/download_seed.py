"""Download seed audio from YouTube

Downloads a short clip to use as reference audio for voice cloning.
"""

import subprocess
from pathlib import Path

KATA_DIR = Path(__file__).parent


def download_seed(url: str = "https://www.youtube.com/watch?v=REuOO4Blwyw", duration: int = 15):
    """Download audio clip from YouTube"""
    output_file = KATA_DIR / "seed.wav"

    print(f"Downloading {duration}s clip from {url}...")

    subprocess.run(
        [
            "yt-dlp",
            "--extract-audio",
            "--audio-format", "wav",
            "--postprocessor-args", f"ffmpeg:-ss 0 -t {duration}",
            "-o", str(output_file),
            url,
        ],
        check=True,
    )

    print(f"Downloaded: {output_file}")
    return output_file


if __name__ == "__main__":
    download_seed()
