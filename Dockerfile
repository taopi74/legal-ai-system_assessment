FROM python:3.11-slim

WORKDIR /app

# Install system deps for pdfplumber / pdf2image / pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create required runtime dirs
RUN mkdir -p data/chroma data/extracted data/edits data/sample_inputs

EXPOSE 8000

CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
