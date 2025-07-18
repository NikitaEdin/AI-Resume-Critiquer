import streamlit as st
import PyPDF2
import io
import os
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Streamlit initialisation
st.set_page_config(page_title="AI Resume Critiquer", layout="centered")
st.title("AI Resume Critiquer")
st.markdown("Upload your resume in PDF format and get feedback from our AI critiquer.")

# Get OpenAI API key from env
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    st.error("OpenAI API key is not set. Please set it in the .env file.")

# File uploader for PDF/TXT files
uploaded_file = st.file_uploader("Choose a PDF/TXT file", type=["pdf", "txt"])
job_role = st.text_input("Enter the job role you are applying for (optional): ")

analyse = st.button("Analyse Resume")


def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

def extract_text_from_file(uploaded_file):
    if uploaded_file is None:
        st.error("Please upload a file to analyse.")
        return None
    
    # PDF
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(io.BytesIO(uploaded_file.read()))
    # TXT
    elif uploaded_file.type == "text/plain":
        return uploaded_file.read().decode("utf-8")
    # Unsupported type
    else:
        st.error("Unsupported file type. Please upload a PDF or TXT file.")
        return None

# Analyse uploaded file
if analyse and uploaded_file is not None:
    st.write("Analysing your resume...")
    try:
        file_content = extract_text_from_file(uploaded_file)
        
        # Check if empty
        if not file_content.strip():
            st.error("The uploaded file is empty or could not be read.")
            st.stop()

        # Prompt structure
        prompt = f"""Please analyse this resume and provide constructive but concise feedback.
        Use UK wording and spelling.

        Focus on the following aspects:
        1. Content clarity and impact.
        2. Skills presentation and relevance to the job role.
        3. Experience and education sections.
        4. No colours or images, following a simple, professional format.
        5. Resume must include relevant links to online profiles (e.g., LinkedIn, GitHub).
        6. Specific improvements for {job_role if job_role else "general job applications"}.

        Resume content:
        {file_content}

        Provide a concise, high-impact critique of this resume. Prioritise the most important points. Limit to the top 5 suggestions only.
        Keep your response under 300 words.
        Use bullet points or headers to structure feedback clearly. 
        """

        # Define ANTHROPIC client
        ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
        client = Anthropic(api_key=ANTHROPIC_API_KEY)
        response = client.messages.create(
            model="claude-opus-4-20250514",  
            max_tokens=500,
            temperature=0.3,
            system="You are an expert resume critiquer and reviewer with years of experience in the field.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        st.markdown("### Analysis Results:")

        # Anthropic
        analysis = "".join(
            block.text if hasattr(block, "text") else str(block)
            for block in response.content
        )
        st.markdown(analysis, unsafe_allow_html=False)
    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")

        
