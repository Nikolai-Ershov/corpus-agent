
def chunk(text: str) -> list[str]:
    chunks = text.split("\n\n")

    res = []
    for part in chunks:
        if part.strip():
            res.append(part.strip())

    return res
