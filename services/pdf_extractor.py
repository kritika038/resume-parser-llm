"""
PDF extraction service for resume processing.
Handles extraction of text from PDF files.
"""

from PyPDF2 import PdfReader
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def extract_pdf(file_object) -> Optional[str]:
    """
    Extracts text from PDF resume.
    
    Processes all pages and concatenates text content.
    
    Args:
        file_object: File-like object from Streamlit uploader (file.BytesIO)
        
    Returns:
        str: Concatenated text from all pages
        None: If extraction fails
        
    Examples:
        >>> with open("resume.pdf", "rb") as f:
        ...     text = extract_pdf(f)
        ...     print(len(text))  # Character count
    """
    try:
        if not file_object:
            logger.warning("No file object provided")
            return None
        
        reader = PdfReader(file_object)
        
        if not reader.pages:
            logger.warning("PDF contains no pages")
            return None
        
        text = ""
        for page_num, page in enumerate(reader.pages):
            try:
                content = page.extract_text()
                if content:
                    text += content + "\n"
            except Exception as e:
                logger.warning(f"Error extracting page {page_num}: {e}")
                continue
        
        if not text.strip():
            logger.warning("No text extracted from PDF")
            return None
        
        logger.info(f"Successfully extracted {len(text)} characters from PDF")
        return text
    
    except Exception as e:
        logger.error(f"PDF extraction failed: {e}")
        return None


def validate_pdf(file_object) -> bool:
    """
    Validates that a file is a readable PDF.
    
    Args:
        file_object: File-like object
        
    Returns:
        bool: True if valid PDF
    """
    try:
        reader = PdfReader(file_object)
        return len(reader.pages) > 0
    except Exception as e:
        logger.error(f"PDF validation failed: {e}")
        return False
