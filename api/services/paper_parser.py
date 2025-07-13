import requests
import fitz  # PyMuPDF

def parse_paper_from_url(paper_url: str) -> dict:
    """
    Fetches a PDF from a URL and extracts its text content.

    Args:
        paper_url: The public URL to the PDF.

    Returns:
        A dictionary containing the text content or an error.
    """
    try:
        response = requests.get(paper_url)
        response.raise_for_status()
        pdf_content = response.content

        text_content = ""
        with fitz.open(stream=pdf_content, filetype="pdf") as doc:
            for page in doc:
                text_content += page.get_text()
        
        return {'success': True, 'text_content': text_content}

    except requests.exceptions.RequestException as e:
        return {'error': f"Failed to fetch paper: {e}"}
    except Exception as e:
        return {'error': f"Failed to parse PDF: {e}"}
