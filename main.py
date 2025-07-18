import streamlit as st
import PyPDF2
import io
from llm_handler import get_available_models, get_selected_model, call_llm
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Streamlit initialisation
st.set_page_config(page_title="AI Resume Critiquer", layout="centered")
st.title("AI Resume Critiquer")
st.markdown("Upload your resume in PDF format and get feedback from our AI critiquer.")

# Get available models
available_models = get_available_models()

# No available models found
if not available_models:
    st.error("No valid API keys found. Please set them in the .env file.")
    st.stop()

use_custom_selection = False
user_selection = None





# Model selection
st.markdown("### Select AI Model")
if len(available_models) > 1:
    use_custom_selection = st.checkbox("Choose AI model manually")
    if use_custom_selection:
        user_selection = st.selectbox("Select the AI model to use:", available_models)

selected_model = get_selected_model(available_models, use_custom_selection, user_selection)
st.info(f"Using AI model: **{selected_model}**")



# File uploader for PDF/TXT files
st.markdown("### Upload Your Resume")
uploaded_file = st.file_uploader("Choose a PDF/TXT file", type=["pdf", "txt"])
job_role = st.text_input("Enter the job role you are applying for (optional): ")

analyse = st.button("Analyse Resume")

# Extract text from PDF files
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

# Extract text based on type
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

        # Call the selected LLM
        analysis = call_llm(selected_model, prompt)

        st.markdown("### Analysis Results:")
        st.markdown(analysis, unsafe_allow_html=False)
    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")
