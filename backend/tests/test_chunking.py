import pytest

from app.services.chunking_service import split_text


def test_split_text_returns_single_chunk_for_short_text():
    text = "AIOS processes enterprise documents."

    chunks = split_text(
        text=text,
        chunk_size=100,
        overlap=20,
    )

    assert chunks == [
        "AIOS processes enterprise documents."
    ]


def test_split_text_creates_multiple_chunks():
    text = "A" * 250

    chunks = split_text(
        text=text,
        chunk_size=100,
        overlap=20,
    )

    assert len(chunks) > 1
    assert all(len(chunk) <= 100 for chunk in chunks)


def test_split_text_applies_overlap():
    text = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    chunks = split_text(
        text=text,
        chunk_size=10,
        overlap=3,
    )

    assert chunks[0][-3:] == chunks[1][:3]


def test_split_text_returns_empty_list_for_empty_text():
    chunks = split_text(
        text="",
        chunk_size=100,
        overlap=20,
    )

    assert chunks == []


def test_split_text_rejects_zero_chunk_size():
    with pytest.raises(
        ValueError,
        match="chunk_size must be greater than zero",
    ):
        split_text(
            text="test",
            chunk_size=0,
            overlap=0,
        )


def test_split_text_rejects_negative_overlap():
    with pytest.raises(
        ValueError,
        match="overlap cannot be negative",
    ):
        split_text(
            text="test",
            chunk_size=100,
            overlap=-1,
        )


def test_split_text_rejects_overlap_equal_to_chunk_size():
    with pytest.raises(
        ValueError,
        match="overlap must be smaller than chunk_size",
    ):
        split_text(
            text="test",
            chunk_size=100,
            overlap=100,
        )
