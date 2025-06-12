import os
import tempfile
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain_google_genai import ChatGoogleGenerativeAI
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import io

load_dotenv()

class text_summarizer:
    def __init__(self, file_path, api_key):
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash",
                                        google_api_key=api_key)
        self.file_path = file_path
    
    def load_document(self):
        """Load document based on file extension"""
        file_extension = Path(self.file_path).suffix.lower()
        
        if file_extension == '.pdf':
            loader = PyPDFLoader(self.file_path)
        elif file_extension in ['.docx', '.doc']:
            loader = Docx2txtLoader(self.file_path)
        elif file_extension == '.txt':
            loader = TextLoader(self.file_path, encoding='utf-8')
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
        
        return loader.load_and_split()
    
    def summarize(self):
        try:
            docs = self.load_document()
            split_docs = RecursiveCharacterTextSplitter(chunk_size=6500, chunk_overlap=400).split_documents(docs)

            chain = load_summarize_chain(
                llm=self.llm,
                chain_type="refine",
                verbose=False,
            )

            output_summary = chain.invoke({"input_documents": split_docs}, return_only_outputs=True)
            return output_summary['output_text']
        except Exception as e:
            return f"Error summarizing document: {str(e)}"

def create_pdf_summary(summary_text, original_filename):
    """Create a PDF from the summary text"""
    buffer = io.BytesIO()
    
    # Create PDF document
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                          rightMargin=72, leftMargin=72,
                          topMargin=72, bottomMargin=18)
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    
    # Build PDF content
    story = []
    
    # Add title
    title = Paragraph(f"Summary of {original_filename}", title_style)
    story.append(title)
    story.append(Spacer(1, 12))
    
    # Add summary content
    # Split text into paragraphs and add each as a separate Paragraph object
    paragraphs = summary_text.split('\n\n')
    for para in paragraphs:
        if para.strip():
            p = Paragraph(para.strip(), styles['Normal'])
            story.append(p)
            story.append(Spacer(1, 12))
    
    # Build PDF
    doc.build(story)
    
    # Get PDF data
    pdf_data = buffer.getvalue()
    buffer.close()
    
    return pdf_data

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

if __name__ == "__main__":
    # This section is no longer needed as Streamlit will handle the app execution
    pass