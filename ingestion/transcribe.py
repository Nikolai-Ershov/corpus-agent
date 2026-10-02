from faster_whisper import WhisperModel


class Transcriber:
    def __init__(self):
        self.model = WhisperModel("large-v3", device="cpu", compute_type="int8")

    def transcribe(self, path: str) -> str:
        segments, info = self.model.transcribe(path, language="ru", vad_filter=True)

        words_per_chunk = 150
        paragraphs = []
        current_words = []

        for segment in segments:
            current_words.extend(segment.text.strip().split())

            if len(current_words) >= words_per_chunk:
                paragraphs.append(" ".join(current_words))
                current_words = []

        if current_words:
            paragraphs.append(" ".join(current_words))

        text = "\n\n".join(paragraphs)
        return text
