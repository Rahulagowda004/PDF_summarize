import os
import tempfile
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain_google_genai import ChatGoogleGenerativeAI
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