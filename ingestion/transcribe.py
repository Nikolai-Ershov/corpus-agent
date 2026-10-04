from faster_whisper import WhisperModel


class Transcriber:
    def __init__(self):
        self.model = WhisperModel("large-v3", device="cpu", compute_type="int8")

    def transcribe(self, path: str):
        segments, info = self.model.transcribe(
            path,
            language="ru",
            vad_filter=True,
            condition_on_previous_text=False,
        )
        total = info.duration

        words_per_chunk = 150
        current_words = []

        for segment in segments:
            current_words.extend(segment.text.strip().split())

            if len(current_words) >= words_per_chunk:
                yield " ".join(current_words), segment.end / total
                current_words = []

        if current_words:
            yield " ".join(current_words), 1.0
