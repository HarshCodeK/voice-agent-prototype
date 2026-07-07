from faster_whisper import WhisperModel
from src.config import WHISPER_MODEL_SIZE
import numpy as np
import wave
import struct

_model = None

def _get_model():
    global _model
    if _model is None:
        _model = WhisperModel(WHISPER_MODEL_SIZE, device="cpu", compute_type="int8")
    return _model

def warmup():
    model = _get_model()
    silence = np.zeros(16000, dtype=np.float32)
    segments, _ = model.transcribe(silence, language="en")
    for _ in segments:
        pass

def transcribe(audio_file_path: str) -> str:
    model = _get_model()
    segments, _ = model.transcribe(audio_file_path)
    return " ".join(seg.text for seg in segments)
