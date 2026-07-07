from faster_whisper import WhisperModel
from src.config import WHISPER_MODEL_SIZE

_model = None

def _get_model():
    global _model
    if _model is None:
        _model = WhisperModel(WHISPER_MODEL_SIZE, device="cpu", compute_type="int8")
    return _model

def transcribe(audio_file_path: str) -> str:
    model = _get_model()
    segments, _ = model.transcribe(audio_file_path)
    return " ".join(seg.text for seg in segments)
