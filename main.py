import streamlit as st
from text_extractor import extract_text_from_file
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
uploaded_file = st.file_uploader("Choose a PDF/TXT/DOCX file", type=["pdf", "txt", "docx"])
job_role = st.text_input("Enter the job role you are applying for (optional): ")

analyse = st.button("Analyse Resume")

# Cache analysis function to avoid repeated calls
@st.cache_data(show_spinner=False)
def get_analysis(model, prompt):
    return call_llm(model, prompt)


# Analyse uploaded file
if analyse and uploaded_file is not None:
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

        # Show spinner while calling LLM
        with st.spinner("Getting AI feedback..."):
            # Call the selected LLM
            analysis = get_analysis(selected_model, prompt)

        st.markdown("### Analysis Results:")
        st.markdown(analysis, unsafe_allow_html=False)

         # Add download button for analysis text
        st.download_button(
            label="Download Analysis as TXT",
            data=analysis,
            file_name="resume_analysis.txt",
            mime="text/plain",
        )
    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")
