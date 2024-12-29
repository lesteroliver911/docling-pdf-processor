import os
os.environ['OMP_NUM_THREADS'] = '4'  # Limit to 4 CPU threads
import streamlit as st
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions, 
    TableFormerMode,
    AcceleratorOptions
)
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
from docling.utils.export import generate_multimodal_pages
import tempfile
from pathlib import Path
import pandas as pd
import datetime
import io

# Define image resolution scale for better quality
IMAGE_RESOLUTION_SCALE = 2.0

def initialize_converter():
    """Initialize the Docling document converter with PDF settings"""
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = True
    pipeline_options.do_table_structure = True
    pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE
    pipeline_options.table_structure_options.do_cell_matching = False
    pipeline_options.accelerator_options = AcceleratorOptions(num_threads=4)
    
    # Image handling options - only use supported options
    pipeline_options.images_scale = IMAGE_RESOLUTION_SCALE
    pipeline_options.generate_page_images = True
    
    # Remove unsupported options
    # pipeline_options.extract_images = True  # This was causing the error
    # pipeline_options.image_options = {      # This might not be supported
    #     'dpi': 300,
    #     'extract_images': True,
    #     'generate_thumbnails': True
    # }

    return DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pipeline_options,
                backend=PyPdfiumDocumentBackend
            )
        }
    )

def process_pdf(uploaded_file, doc_converter):
    """Process the uploaded PDF file and return markdown and multimodal content"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name

    try:
        # Convert the PDF
        conversion_result = doc_converter.convert(
            tmp_path,
            max_num_pages=100,
            max_file_size=20971520
        )
        
        # Get markdown content
        markdown_content = conversion_result.document.export_to_markdown()
        
        # Generate multimodal content
        multimodal_pages = []
        for (content_text, content_md, content_dt, page_cells, page_segments, page) in generate_multimodal_pages(conversion_result):
            try:
                # Get the page image
                if hasattr(page, 'image') and page.image is not None:
                    # Convert PIL image to bytes for Streamlit
                    img_bytes = io.BytesIO()
                    page.image.save(img_bytes, format='PNG')
                    img_bytes = img_bytes.getvalue()
                    st.write(f"Successfully processed image for page {page.page_no}")  # Debug info
                else:
                    img_bytes = None
                    st.write(f"No image available for page {page.page_no}")  # Debug info
            except Exception as e:
                st.write(f"Error processing image for page {page.page_no}: {str(e)}")  # Debug info
                img_bytes = None

            # Try to get images from the page's extracted images
            extracted_images = getattr(page, 'extracted_images', [])
            if extracted_images:
                st.write(f"Found {len(extracted_images)} extracted images on page {page.page_no}")  # Debug info

            dpi = getattr(page, '_default_image_scale', 1.0) * 72
            multimodal_pages.append({
                "page_number": page.page_no,
                "text_content": content_text,
                "markdown_content": content_md,
                "tables": page_cells,
                "segments": page_segments,
                "image_data": img_bytes,
                "image_info": {
                    "width": page.image.width if hasattr(page, 'image') and page.image is not None else 0,
                    "height": page.image.height if hasattr(page, 'image') and page.image is not None else 0,
                    "dpi": dpi
                }
            })
        
        return markdown_content, multimodal_pages
    except Exception as e:
        st.error(f"Error processing PDF: {str(e)}")
        return None, None
    finally:
        os.unlink(tmp_path)

def main():
    st.set_page_config(
        page_title="PDF Extract with Docling",
        page_icon="📄",
        layout="wide"
    )

    # Remove the main title since we're moving it to sidebar
    doc_converter = initialize_converter()
    uploaded_file = st.file_uploader("Choose a PDF file", type=['pdf'])

    if uploaded_file is not None:
        with st.spinner("Processing PDF with Docling AI..."):
            markdown_content, multimodal_pages = process_pdf(uploaded_file, doc_converter)
            
            if markdown_content and multimodal_pages:
                tab1, tab2, tab3 = st.tabs(["AI Preview", "Extracted Content", "Document Analysis"])
                
                with tab1:
                    st.markdown("### AI-Generated Preview")
                    st.markdown(markdown_content)
                
                with tab2:
                    st.markdown("### Extracted Content")
                    st.text_area(
                        "AI-Processed Content",
                        value=markdown_content,
                        height=500,
                        key="markdown_content"
                    )
                    st.download_button(
                        label="Download Extracted Content",
                        data=markdown_content,
                        file_name=f"{Path(uploaded_file.name).stem}.md",
                        mime="text/markdown"
                    )
                
                with tab3:
                    st.subheader("AI Document Analysis")
                    for page in multimodal_pages:
                        with st.expander(f"Page {page['page_number']} Analysis"):
                            col1, col2 = st.columns(2)
                            with col1:
                                if page['image_data']:
                                    st.image(
                                        page['image_data'], 
                                        caption=f"AI-Processed Page {page['page_number']}", 
                                        use_container_width=True
                                    )
                                st.markdown("#### Document Metrics")
                                st.json(page['image_info'])
                                if page['tables']:
                                    st.markdown("#### AI-Detected Tables")
                                    st.json(page['tables'])
                            with col2:
                                st.markdown("#### Processed Content")
                                st.markdown(page['markdown_content'])
    else:
        st.info("👆 Upload a PDF file to start AI-powered analysis")

    # Updated sidebar with title and smaller fonts
    with st.sidebar:
        st.markdown("""
        <div style='margin-bottom: 20px;'>
            <h3 style='font-size: 1.2em;'>📄 PDF Extract with Docling</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<h4 style='font-size: 1em;'>About Docling</h4>", unsafe_allow_html=True)
        st.markdown("""
        <div style='font-size: 0.9em;'>
        Docling is an advanced document processing library for extracting structured content from PDFs.
        
        **Key Features:**
        - 📝 Smart Text Extraction
        - 🔍 OCR Processing
        - 📊 Table Detection
        - 📄 Page Analysis
        - 📐 Structure Recognition
        - 🖼️ Image Processing
        - 📑 Multi-Modal Analysis
        
        [Learn more about Docling](https://ds4sd.github.io/docling/)
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("""
        <small style='font-size: 0.8em;'>Built with the Docling document processing library</small>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
