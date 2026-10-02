from index.chunk import chunk


def test_chunk_splits_on_double_newline():
    result = chunk("paragraph1\n\nparagraph2")
    assert result == ["paragraph1", "paragraph2"]


def test_chunk_empty_string():
    result = chunk("")
    assert result == []


def test_chunk_single_paragraph_no_separator():
    result = chunk("a single paragraph with no separator")
    assert result == ["a single paragraph with no separator"]


def test_chunk_strips_whitespace():
    result = chunk("  paragraph1  \n\n  paragraph2  ")
    assert result == ["paragraph1", "paragraph2"]