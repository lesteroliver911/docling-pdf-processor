# Docling-Llama-PDF-AI

A simple UI wrapper around Docling for document processing. I built this to make document analysis more accessible and thought others might find it useful.

Inspired by [Docling](https://github.com/DS4SD/docling) and its integration with [LlamaIndex](https://docs.llamaindex.ai/en/stable/api_reference/readers/docling/).

## What This Does

- Processes PDFs using Docling's document analysis
- Extracts text, tables, and performs OCR
- Presents results in a clean Streamlit interface
- Handles multi-page documents and complex tables
- Makes document processing accessible to non-technical users

## Setup

```bash
git clone https://github.com/lesteroliver911/docling-pdf-processor.git
cd docling-pdf-processor
pip install -r requirements.txt
streamlit run app.py
```

## How It Works

The app combines three powerful frameworks:
- [Docling](https://ds4sd.github.io/docling/v2/): Advanced document processing and analysis
- [LlamaIndex](https://docs.llamaindex.ai/en/stable/): Robust framework for structuring and indexing document data
- Streamlit: Simple web interface

Key functions:

```python
# Setting up the document processor
def initialize_converter():
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = True
    pipeline_options.do_table_structure = True
    return DocumentConverter(...)

# Processing PDFs
def process_pdf(uploaded_file, doc_converter):
    # Handles conversion and extraction
    # Returns markdown and multimodal content
```

## Configuration

You can adjust a few settings in the code:
- `OMP_NUM_THREADS`: CPU threads (default: 4)
- `IMAGE_RESOLUTION_SCALE`: Image quality (default: 2.0)

## Requirements

```
docling
llama-index
streamlit
pandas
python-dotenv
```

## Using the App

1. Upload a PDF
2. Check out the three tabs:
   - AI Preview: Quick look at the content
   - Extracted Content: Full text and structure
   - Document Analysis: Page-by-page breakdown

## Notes

- Works best with clearly formatted PDFs
- Table extraction might need tweaking for complex layouts
- OCR can be slow on large documents
- Docling provides robust document processing - check their [documentation](https://ds4sd.github.io/docling/v2/) for more features
- LlamaIndex integration adds powerful document structuring capabilities - see their [Docling reader docs](https://docs.llamaindex.ai/en/stable/api_reference/readers/docling/)

Feel free to use this code, modify it, or suggest improvements. You can find me on [LinkedIn](https://www.linkedin.com/in/lesteroliver/) if you want to discuss Python, AI, or document processing.

Built by [Your Name]
