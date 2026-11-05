"""Transcribe an audio or video file to text, one file at a time, with
progress written to disk incrementally so a crash doesn't lose the whole run."""

import os

# must come before the Transcriber import below, which pulls in
# faster-whisper/huggingface_hub transitively
os.environ["HF_HUB_OFFLINE"] = "1"

import time
import sys
from pathlib import Path

from ingestion.transcribe import Transcriber


def run(media_path: str) -> None:
    source = Path(media_path)
    target = Path("data/base") / f"{source.stem}.txt"
    partial = target.with_suffix(".txt.part")

    if target.exists():
        # target only ever gets this name once a run finished cleanly (see the
        # rename at the end) — its existence means this file is already done
        print(f"{target} already exists, skipping")
        return

    started = time.time()
    first = True

    with open(partial, "w", encoding="utf-8") as f:
        # Transcriber().transcribe() is a generator, not a single return value:
        # it yields each paragraph as it's produced, so a crash mid-transcription
        # (a 3-hour file failing at minute 40) still leaves everything
        # transcribed up to that point on disk, instead of losing it all
        for paragraph, progress in Transcriber().transcribe(str(source)):
            if not first:
                f.write("\n\n")  # blank line between paragraphs, none before the first
            f.write(paragraph)
            f.flush()  # force it to disk now, not whenever the OS buffer decides to
            first = False

            elapsed = time.time() - started
            # \r + end="" overwrites the same line instead of spamming new ones
            print(f"\r{progress:.0%}  прошло {elapsed / 60:.0f} мин", end="", flush=True)

    # only renamed to its final name once the whole file is done — this is
    # the one moment that makes the `target.exists()` check above reliable
    partial.replace(target)
    print(f"\nSaved to {target}")


if __name__ == "__main__":
    for media_path in sys.argv[1:]:
        try:
            run(media_path)
        except Exception as e:
            # one bad file (corrupt audio, unsupported codec) shouldn't abort
            # the rest of the batch — report it and move on to the next path
            print(f"\nFAILED {media_path}: {type(e).__name__}: {e}")
