from pypdf import PdfReader

def get_text_from_pdf(path: str) -> str:
    """Extract text content from a PDF file.
    
    Args:
        path: Path to the PDF file
        
    Returns:
        Concatenated text from all pages
    """
    r = PdfReader(path)
    return "\n".join(page.extract_text() or "" for page in r.pages)