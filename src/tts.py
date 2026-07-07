import pyttsx3
import os

_engine = None

def _get_engine():
    global _engine
    if _engine is None:
        _engine = pyttsx3.init()
    return _engine

def warmup():
    engine = _get_engine()
    tmp = "warmup_.wav"
    engine.save_to_file("Hello.", tmp)
    engine.runAndWait()
    try:
        os.remove(tmp)
    except OSError:
        pass

def speak(text: str, output_path: str = "response.wav") -> str:
    engine = _get_engine()
    engine.save_to_file(text, output_path)
    engine.runAndWait()
    return output_path
