FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Create documents directory for PDF files
RUN mkdir -p /app/documents

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY main.py .

COPY app.py .

# Set the documents directory as a volume
VOLUME /app/documents

CMD ["streamlit", "run", "app.py"]

# Build Command:
# -----------------------------
# docker build -t rahula004/quicksumm .
#
# Run Command:
# docker run -p 8501:8501 rahula004/quicksumm
# -----------------------------
# For Windows PowerShell:
# docker run -it -v "${PWD}/documents:/app/documents" -e GOOGLE_API_KEY="" -e FILE_PATH="/app/documents/deepseek.pdf" rahula004/quicksumm