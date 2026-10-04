import os
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
        print(f"{target} already exists, skipping")
        return

    started = time.time()
    first = True

    with open(partial, "w", encoding="utf-8") as f:
        for paragraph, progress in Transcriber().transcribe(str(source)):
            if not first:
                f.write("\n\n")
            f.write(paragraph)
            f.flush()
            first = False

            elapsed = time.time() - started
            print(f"\r{progress:.0%}  прошло {elapsed / 60:.0f} мин", end="", flush=True)

    partial.replace(target)
    print(f"\nSaved to {target}")


if __name__ == "__main__":
    for media_path in sys.argv[1:]:
        try:
            run(media_path)
        except Exception as e:
            print(f"\nFAILED {media_path}: {type(e).__name__}: {e}")
