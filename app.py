import os
import tempfile
from pathlib import Path
import streamlit as st
from main import text_summarizer, create_pdf_summary

# Streamlit App
with st.sidebar:
    google_api_key = st.text_input("Google API Key", key="google_api_key", type="password")
    "[Get a Google API key](https://makersuite.google.com/app/apikey)"
    "[View the source code](https://github.com/your-repo/PDF_summarize)"

st.title("📄 Document Summarizer")
st.caption("🚀 A Streamlit app powered by Google Gemini to summarize PDF, DOCX, and text documents")

# File upload
uploaded_file = st.file_uploader(
    "Choose a document file", 
    type=["pdf", "docx", "doc", "txt"],
    help="Supported formats: PDF, Word documents (DOCX/DOC), and text files (TXT)"
)

if uploaded_file is not None:
    if not google_api_key:
        st.info("Please add your Google API key to continue.")
        st.stop()
    
    # Save uploaded file to temporary location with proper extension
    file_extension = Path(uploaded_file.name).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name
    
    st.success(f"File '{uploaded_file.name}' uploaded successfully!")
    
    if st.button("Generate Summary"):
        with st.spinner("Summarizing document... This may take a few minutes."):
            try:
                summarizer = text_summarizer(tmp_file_path, google_api_key)
                summary = summarizer.summarize()
                
                st.subheader("📋 Summary")
                st.write(summary)
                
                # Create PDF summary
                filename_without_ext = Path(uploaded_file.name).stem
                pdf_data = create_pdf_summary(summary, uploaded_file.name)
                
                # Add download button for PDF summary
                st.download_button(
                    label="📥 Download Summary as PDF",
                    data=pdf_data,
                    file_name=f"{filename_without_ext}_summary.pdf",
                    mime="application/pdf",
                    help="Download the summary as a PDF file"
                )
                
                # Clean up temporary file
                os.unlink(tmp_file_path)
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                # Clean up temporary file even if error occurs
                if os.path.exists(tmp_file_path):
                    os.unlink(tmp_file_path)
