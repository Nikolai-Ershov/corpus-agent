"""Tests for chunk()."""

from index.chunk import chunk


def test_chunk_splits_on_double_newline():
    """Two paragraphs separated by a double newline should come back
    as two separate chunks."""
    result = chunk("paragraph1\n\nparagraph2")
    assert result == ["paragraph1", "paragraph2"]


def test_chunk_empty_string():
    """An empty string has no paragraphs to split — the result should
    be an empty list, not a list containing one empty chunk."""
    result = chunk("")
    assert result == []


def test_chunk_single_paragraph_no_separator():
    """No double newline anywhere in the text means nothing to split
    on — the whole string comes back as a single chunk."""
    result = chunk("a single paragraph with no separator")
    assert result == ["a single paragraph with no separator"]


def test_chunk_strips_whitespace():
    """Leading/trailing whitespace around each paragraph should be
    stripped from the resulting chunks."""
    result = chunk("  paragraph1  \n\n  paragraph2  ")
    assert result == ["paragraph1", "paragraph2"]