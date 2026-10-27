"""Unit tests for PDF validation, chunking, and keyword retrieval."""

import pytest
from services.pdf_service import (
    validate_pdf_file,
    chunk_document_pages,
    retrieve_relevant_chunks,
    MAX_PDF_SIZE_BYTES,
)


def test_validate_pdf_file():
    ok, _ = validate_pdf_file("syllabus.pdf", b"%PDF-1.4 dummy bytes")
    assert ok is True

    bad_ext, msg = validate_pdf_file("notes.docx", b"test")
    assert bad_ext is False
    assert "Only PDF documents" in msg

    empty, msg = validate_pdf_file("empty.pdf", b"")
    assert empty is False
    assert "empty" in msg

    oversized, msg = validate_pdf_file("huge.pdf", b"x" * (MAX_PDF_SIZE_BYTES + 1024))
    assert oversized is False
    assert "exceeds limit" in msg


def test_chunk_document_pages():
    pages = [
        {"page_number": 1, "text": "Page one introduction to computer memory and cache hierarchy."},
        {"page_number": 2, "text": "Page two discussing virtual memory, page tables, and TLB buffers."},
    ]
    chunks = chunk_document_pages(pages, chunk_size=50, overlap=10)
    assert len(chunks) >= 2
    assert chunks[0]["page_number"] == 1
    assert "content" in chunks[0]


def test_retrieve_relevant_chunks():
    chunks = [
        {"id": 1, "page_number": 1, "content": "The CPU uses cache to reduce average memory access latency."},
        {"id": 2, "page_number": 2, "content": "Relational databases use B-tree indices to speed up queries."},
        {"id": 3, "page_number": 3, "content": "Convolutional neural networks process image feature maps."},
    ]

    result = retrieve_relevant_chunks("How does CPU cache memory work?", chunks, top_k=1)
    assert "[Source: Page 1]" in result
    assert "cache" in result
