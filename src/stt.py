import os

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from faster_whisper import WhisperModel
from src.config import WHISPER_MODEL_SIZE

_model = None

def _get_model():
    global _model
    if _model is None:
        _model = WhisperModel(WHISPER_MODEL_SIZE, device="cpu", compute_type="int8")
    return _model

def warmup():
    _get_model()

def transcribe(audio_file_path: str) -> str:
    model = _get_model()
    segments, _ = model.transcribe(audio_file_path)
    return " ".join(seg.text for seg in segments)
