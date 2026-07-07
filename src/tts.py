import asyncio
import edge_tts
import os

VOICE = "en-US-AriaNeural"

def speak(text: str, output_path: str = "response.wav") -> str:
    async def _run():
        communicate = edge_tts.Communicate(text, VOICE)
        await communicate.save(output_path)
    asyncio.run(_run())
    return output_path

def warmup():
    speak("Hello.")
