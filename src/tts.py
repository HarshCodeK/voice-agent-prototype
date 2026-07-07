import pyttsx3

_engine = None

def _get_engine():
    global _engine
    if _engine is None:
        _engine = pyttsx3.init()
    return _engine

def speak(text: str, output_path: str = "response.wav") -> str:
    engine = _get_engine()
    engine.save_to_file(text, output_path)
    engine.runAndWait()
    return output_path
