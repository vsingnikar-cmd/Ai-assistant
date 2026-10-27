"""PDF Study Assistant UI Component.

Enables students to upload syllabus, lecture slides, and notes (PDF),
extracts text with PyMuPDF, chunks content, and answers queries grounded
in the document with specific page citations.
"""

from typing import Any, Dict
import streamlit as st
from agent.academic_agent import AcademicAgent
from services.pdf_service import extract_text_from_pdf_bytes, retrieve_relevant_chunks


def render_pdf_assistant(student_profile: Dict[str, Any], user_id: str):
    """Render PDF Upload and Grounded Document Q&A."""
    st.title("📄 PDF Study Assistant")
    st.caption("Upload course notes, textbook chapters, or question banks and ask grounded questions.")

    agent = AcademicAgent(user_id=user_id)

    # File Uploader
    uploaded_file = st.file_uploader(
        "Upload Study PDF (Max 15MB)",
        type=["pdf"],
        help="Upload lecture notes, textbook chapters, or exam syllabus in PDF format.",
    )

    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        current_loaded = st.session_state.get("active_pdf_name")

        # Parse only when a new file is uploaded
        if current_loaded != uploaded_file.name:
            with st.spinner("Extracting text and building document search index with PyMuPDF..."):
                res = agent.extract_pdf_text(file_bytes, uploaded_file.name)
                if not res.get("success"):
                    st.error(res.get("message"))
                    st.session_state.active_pdf_chunks = []
                    st.session_state.active_pdf_name = None
                else:
                    st.success(f"Loaded '{uploaded_file.name}': {res.get('total_pages')} pages extracted.")
                    st.session_state.active_pdf_chunks = res.get("chunks", [])
                    st.session_state.active_pdf_name = uploaded_file.name
                    st.session_state.active_pdf_pages = res.get("total_pages", 0)

    # Document Status Card
    active_pdf = st.session_state.get("active_pdf_name")
    chunks = st.session_state.get("active_pdf_chunks", [])
    pages = st.session_state.get("active_pdf_pages", 0)

    if active_pdf and chunks:
        st.markdown(
            f"""
            <div style="background: #1e293b; border-left: 4px solid #3b82f6; border-radius: 6px; padding: 12px 16px; margin: 16px 0;">
                <span style="color: #94a3b8; font-size: 0.85rem;">Active Document:</span>
                <h4 style="margin: 2px 0 0 0; color: #f8fafc;">📑 {active_pdf} ({pages} Pages • {len(chunks)} Chunks)</h4>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.subheader("❓ Ask Questions About This Document")
        doc_query = st.text_input(
            "Document Query",
            placeholder="e.g. What are the key features described on page 3? Explain the algorithm mentioned.",
        )

        col_btn1, col_btn2 = st.columns([1, 4])
        with col_btn1:
            ask_btn = st.button("Search & Answer", type="primary", use_container_width=True)

        if ask_btn and doc_query:
            with st.spinner("Retrieving relevant passages and synthesizing verified answer..."):
                # 1. Retrieve top relevant chunks
                relevant_context = agent.retrieve_document_context(doc_query, chunks, top_k=4)

                # 2. Query Gemini with strict grounding instructions
                success, answer = agent.answer_academic_query(
                    query=doc_query,
                    document_context=relevant_context,
                    document_name=active_pdf,
                )

                if success:
                    st.markdown("### 🎓 Document Grounded Answer")
                    st.markdown(answer)

                    # Expandable source context for transparency
                    with st.expander("🔍 View Retrieved Excerpts from PDF"):
                        st.markdown(relevant_context)
                else:
                    st.error(answer)
    else:
        st.info("👆 Please upload a PDF study document above to begin document-grounded question answering.")
