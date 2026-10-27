"""PDF Processing and Grounded Retrieval Service.

Extracts text page-by-page using PyMuPDF (fitz), detects image-only / scanned PDFs,
segments text into searchable chunks with source page attribution, and performs
relevance scoring for document-grounded question answering.
"""

import re
from typing import Any, Dict, List, Optional

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    fitz = None  # type: ignore
    PYMUPDF_AVAILABLE = False

MAX_PDF_SIZE_MB = 15
MAX_PDF_SIZE_BYTES = MAX_PDF_SIZE_MB * 1024 * 1024


def validate_pdf_file(filename: str, file_bytes: bytes) -> tuple[bool, str]:
    """Validate file extension and size constraints."""
    if not filename.lower().endswith(".pdf"):
        return False, "Invalid file format. Only PDF documents (.pdf) are supported."
    if len(file_bytes) > MAX_PDF_SIZE_BYTES:
        return False, f"File size exceeds limit of {MAX_PDF_SIZE_MB}MB."
    if len(file_bytes) == 0:
        return False, "Uploaded PDF file is empty (0 bytes)."
    return True, ""


def extract_text_from_pdf_bytes(pdf_bytes: bytes, filename: str) -> Dict[str, Any]:
    """Extract text page-by-page using PyMuPDF.

    Returns:
        Dict with keys:
        - success (bool)
        - message (str)
        - pages (list of dicts with page_number and text)
        - total_pages (int)
        - is_scanned (bool)
        - chunks (list of searchable chunks with page attribution)
    """
    is_valid, err_msg = validate_pdf_file(filename, pdf_bytes)
    if not is_valid:
        return {"success": False, "message": err_msg, "pages": [], "chunks": []}

    if not PYMUPDF_AVAILABLE:
        return {
            "success": False,
            "message": "PyMuPDF library is not installed in the Python environment.",
            "pages": [],
            "chunks": [],
        }

    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        pages_data = []
        total_text_length = 0

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text").strip()
            total_text_length += len(text)
            pages_data.append({
                "page_number": page_num + 1,
                "text": text,
            })

        doc.close()

        # Scanned PDF detection: if total characters across all pages is negligible
        if total_text_length < 50 and len(pages_data) > 0:
            return {
                "success": False,
                "message": (
                    "The uploaded PDF appears to be a scanned document or contains only images "
                    "without selectable text. Please upload a digital PDF containing searchable text layers."
                ),
                "pages": pages_data,
                "total_pages": len(pages_data),
                "is_scanned": True,
                "chunks": [],
            }

        # Chunk documents
        chunks = chunk_document_pages(pages_data, chunk_size=800, overlap=150)

        return {
            "success": True,
            "message": f"Successfully extracted {len(pages_data)} pages ({len(chunks)} chunks).",
            "filename": filename,
            "pages": pages_data,
            "total_pages": len(pages_data),
            "is_scanned": False,
            "chunks": chunks,
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to parse PDF document: {str(e)[:150]}",
            "pages": [],
            "chunks": [],
        }


def chunk_document_pages(pages: List[Dict[str, Any]], chunk_size: int = 800, overlap: int = 150) -> List[Dict[str, Any]]:
    """Split text into overlapping passages with page number metadata."""
    chunks = []
    chunk_id = 1

    for p in pages:
        page_num = p["page_number"]
        text = p["text"]
        if not text:
            continue

        # Clean excess whitespace
        clean_text = re.sub(r"\s+", " ", text).strip()
        if len(clean_text) <= chunk_size:
            chunks.append({
                "id": chunk_id,
                "page_number": page_num,
                "content": clean_text,
            })
            chunk_id += 1
            continue

        # Overlapping sliding window
        start = 0
        while start < len(clean_text):
            end = start + chunk_size
            chunk_slice = clean_text[start:end]

            # Try to break on a sentence or period boundary if practical
            if end < len(clean_text):
                last_period = chunk_slice.rfind(". ")
                if last_period > chunk_size // 2:
                    chunk_slice = chunk_slice[: last_period + 1]
                    end = start + len(chunk_slice)

            chunks.append({
                "id": chunk_id,
                "page_number": page_num,
                "content": chunk_slice.strip(),
            })
            chunk_id += 1
            start = end - overlap

    return chunks


def retrieve_relevant_chunks(query: str, chunks: List[Dict[str, Any]], top_k: int = 6) -> str:
    """Retrieve relevant chunks matching the query using keyword/lexical frequency scoring.

    Supports 2-letter abbreviations (e.g. AR, VR, MR, AI, ML, OS) and guarantees multi-concept
    coverage when questions ask about multiple entities.
    Formats the retrieved excerpts with strict [Page X] headers.
    """
    if not chunks:
        return "No document text available."

    # For standard academic notes / chapters (<= 20 chunks), provide all excerpts
    # so the LLM has comprehensive context across all sections and concepts.
    if len(chunks) <= 20:
        return "\n\n---\n\n".join(
            f"[Source: Page {c['page_number']}]\n{c['content']}" for c in chunks
        )

    query_words = set(re.findall(r"\b[a-zA-Z0-9_]{2,}\b", query.lower()))
    # Remove common English stop words
    stop_words = {"the", "is", "at", "which", "on", "a", "an", "and", "or", "in", "to", "what", "how", "why", "are", "for"}
    keywords = [w for w in query_words if w not in stop_words]

    if not keywords:
        selected = chunks[:min(top_k, len(chunks))]
        return "\n\n---\n\n".join(
            f"[Source: Page {c['page_number']}]\n{c['content']}" for c in selected
        )

    # Multi-term guarantee: ensure each distinct keyword gets its best matching chunk
    selected_chunk_ids = set()
    selected_chunks = []

    for kw in keywords:
        best_match = None
        best_count = 0
        for chunk in chunks:
            count = chunk["content"].lower().count(kw)
            if count > best_count:
                best_count = count
                best_match = chunk
        if best_match and best_match["id"] not in selected_chunk_ids:
            selected_chunk_ids.add(best_match["id"])
            selected_chunks.append(best_match)

    # Also sort all chunks by aggregate score to fill remaining slots
    scored_chunks = []
    for chunk in chunks:
        content_lower = chunk["content"].lower()
        score = sum(content_lower.count(kw) * 2 for kw in keywords)
        scored_chunks.append((score, chunk))

    scored_chunks.sort(key=lambda x: x[0], reverse=True)

    for score, chunk in scored_chunks:
        if len(selected_chunks) >= max(top_k, len(keywords) * 2):
            break
        if chunk["id"] not in selected_chunk_ids and score > 0:
            selected_chunk_ids.add(chunk["id"])
            selected_chunks.append(chunk)

    if not selected_chunks:
        selected_chunks = chunks[:min(top_k, len(chunks))]

    # Sort selected by original page number and id for coherent reading flow
    selected_chunks.sort(key=lambda c: (c["page_number"], c["id"]))

    formatted_context = []
    for c in selected_chunks:
        formatted_context.append(f"[Source: Page {c['page_number']}]\n{c['content']}")

    return "\n\n---\n\n".join(formatted_context)
