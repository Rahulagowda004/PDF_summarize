import os
import tempfile
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain_google_genai import ChatGoogleGenerativeAI
import streamlit as st

load_dotenv()

class text_summarizer:
    def __init__(self, file_path, api_key):
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash",
                                        google_api_key=api_key)
        self.file_path = file_path
    
    def summarize(self):
        try:
            loader = PyPDFLoader(self.file_path)
            docs = loader.load_and_split()
            split_docs = RecursiveCharacterTextSplitter(chunk_size=6500, chunk_overlap=400).split_documents(docs)

            chain = load_summarize_chain(
                llm=self.llm,
                chain_type="refine",
                verbose=False,
            )

            output_summary = chain.invoke({"input_documents": split_docs}, return_only_outputs=True)
            return output_summary['output_text']
        except Exception as e:
            return f"Error summarizing PDF: {str(e)}"

# Streamlit App
with st.sidebar:
    google_api_key = st.text_input("Google API Key", key="google_api_key", type="password")
    "[Get a Google API key](https://makersuite.google.com/app/apikey)"
    "[View the source code](https://github.com/your-repo/PDF_summarize)"

st.title("📄 PDF Summarizer")
st.caption("🚀 A Streamlit app powered by Google Gemini to summarize PDF documents")

# File upload
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    if not google_api_key:
        st.info("Please add your Google API key to continue.")
        st.stop()
    
    # Save uploaded file to temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name
    
    st.success(f"File '{uploaded_file.name}' uploaded successfully!")
    
    if st.button("Generate Summary"):
        with st.spinner("Summarizing PDF... This may take a few minutes."):
            try:
                summarizer = text_summarizer(tmp_file_path, google_api_key)
                summary = summarizer.summarize()
                
                st.subheader("📋 Summary")
                st.write(summary)
                
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