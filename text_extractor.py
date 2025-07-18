import io
import PyPDF2
import streamlit as st
from docx import Document

# Extract text from PDF files
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

# Extract text from DOCX files
def extract_text_from_docx(docx_file):
    document = Document(docx_file)
    text = ""
    for paragraph in document.paragraphs:
        text += paragraph.text + "\n"
    return text


# Extract text based on type
def extract_text_from_file(uploaded_file):
    if uploaded_file is None:
        st.error("Please upload a file to analyse.")
        return None
    content_type = uploaded_file.type

    # PDF
    if content_type == "application/pdf":
        return extract_text_from_pdf(io.BytesIO(uploaded_file.read()))
    # TXT
    elif content_type == "text/plain":
        return uploaded_file.read().decode("utf-8")
    # DOCX
    elif content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return extract_text_from_docx(io.BytesIO(uploaded_file.read()))
    # Unsupported type
    else:
        st.error("Unsupported file type. Please upload a PDF or TXT file.")
        return None