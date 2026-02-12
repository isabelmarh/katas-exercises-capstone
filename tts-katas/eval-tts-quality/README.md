# Evaluate TTS Quality

Build an LLM-as-Judge agent that evaluates Text-to-Speech quality.

## Setup

From repo root:
```bash
uv sync --group tts
```

## Generate Audio

```bash
cd tts-katas/eval-tts-quality

# Download reference voice from YouTube (15s clip)
python download_seed.py

# Generate TTS samples using voice cloning
python tts.py
```

This creates:
- `seed.wav` - Original human voice reference
- `sample1.wav` - `sample5.wav` - TTS voice-cloned samples

## Your Task

Build an LLM judge in `main.py` that evaluates the TTS samples in two steps:

1. **Evaluate TTS quality**: Have the LLM assess each sample's quality (naturalness, clarity, etc.)
2. **Compare vs seed**: Have the LLM compare each TTS sample against the original seed voice

Remember: LLMs are bad at numerical scores! Use descriptive/qualitative evaluations.
