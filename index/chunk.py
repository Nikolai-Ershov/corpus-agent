"""Единая структура нарезания на чанки"""


def chunk(text: str) -> list[str]:
    #нарезка происходит по обзацу с двойным переносом
    #текст уже должен быть зарранеее разделён двойнвым отступом
    chunks = text.split("\n\n")

    res = []
    for part in chunks:
        if part.strip():
            res.append(part.strip())

    return res
