"""Splits text into chunks on existing paragraph breaks.

Currently a pass-through: the real chunk-size decision happens earlier,
in ingestion/transcribe.py's word-count accumulation. This just re-splits
on the "\n\n" markers that step already produced."""


def chunk(text: str) -> list[str]:
    # splits strictly on an existing double-newline — assumes the text
    # was already segmented upstream (see ingestion/transcribe.py)
    parts = text.split("\n\n")

    res = []
    for part in parts:
        if part.strip():  # drop any empty/whitespace-only fragment
            res.append(part.strip())

    return res
