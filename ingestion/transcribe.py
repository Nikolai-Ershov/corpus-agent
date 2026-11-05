"""Transcribes audio/video to text using faster-whisper's reimplementation
of OpenAI's Whisper large-v3 model."""

from faster_whisper import WhisperModel


class Transcriber:
    def __init__(self):
        # CPU + int8: no GPU available here; int8 trades some precision
        # for a large speed/memory win, acceptable for this corpus
        self.model = WhisperModel("large-v3", device="cpu", compute_type="int8")

    def transcribe(self, path: str):
        segments, info = self.model.transcribe(
            path,
            language="ru",
            vad_filter=True,  # skip silent stretches instead of transcribing dead air
            # default is True; False here because it was causing Whisper to
            # repeat/hallucinate text by over-anchoring on what it just said
            condition_on_previous_text=False,
        )
        total = info.duration

        # a floor, not a ceiling: we keep accumulating whole segments past
        # 150 words until the current one ends — this is what keeps every
        # chunk boundary on a natural pause instead of mid-sentence. chunk.py
        # is where this gets re-split smaller later; this number stays as is
        words_per_chunk = 150
        current_words = []

        for segment in segments:
            current_words.extend(segment.text.strip().split())

            if len(current_words) >= words_per_chunk:
                yield " ".join(current_words), segment.end / total
                current_words = []

        if current_words:  # whatever's left under threshold at the very end
            yield " ".join(current_words), 1.0