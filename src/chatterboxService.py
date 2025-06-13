# chatterboxservice.py
from chatterbox.tts import ChatterboxTTS
from pathlib import Path

class ChatterboxService:
    def __init__(self, model: ChatterboxTTS, audio_prompt_path: Path):
        self.model = model
        self.audio_prompt_path = audio_prompt_path

    def convert_text_to_voice(self, text: str):
        wav = self.model.generate(text, audio_prompt_path=str(self.audio_prompt_path))
        return wav, self.model.sr
