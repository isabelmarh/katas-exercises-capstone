"""TTS Generator for evaluation kata

Use this to generate audio samples using voice cloning from seed.wav
"""

from pathlib import Path

import soundfile as sf
import torch
from qwen_tts import Qwen3TTSModel

KATA_DIR = Path(__file__).parent


def generate_sample(model, filename: str, text: str, seed_audio: Path) -> Path:
    """Generate a TTS sample using voice cloning"""
    wavs, sr = model.generate_voice_clone(
        text=text,
        language="English",
        ref_audio=str(seed_audio),
        ref_text="",
        x_vector_only_mode=True,
    )
    output_path = KATA_DIR / filename
    sf.write(str(output_path), wavs[0], sr)
    return output_path


if __name__ == "__main__":
    seed_audio = KATA_DIR / "seed.wav"

    if not seed_audio.exists():
        print("Error: seed.wav not found. Run download_seed.py first.")
        exit(1)

    print("Loading TTS model (first run downloads ~3.4GB)...")
    print("This may take several minutes...")
    model = Qwen3TTSModel.from_pretrained(
        "Qwen/Qwen3-TTS-12Hz-1.7B-Base",  # Use Base model for voice cloning
        device_map="cuda:0" if torch.cuda.is_available() else "cpu",
        dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
        attn_implementation="flash_attention_2" if torch.cuda.is_available() else "eager",
    )

    samples = [
        ("sample1.wav", "Good morning! How are you?"),
        ("sample2.wav", "The weather is nice today."),
        ("sample3.wav", "Thank you very much."),
        ("sample4.wav", "I'm excited about this project."),
        ("sample5.wav", "Please have a seat."),
    ]

    print(f"\nGenerating samples using voice from {seed_audio.name}...")
    for filename, text in samples:
        print(f"  {filename}: {text}")
        generate_sample(model, filename, text, seed_audio)

    print("\nDone!")
