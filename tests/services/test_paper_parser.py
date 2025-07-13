import pytest
import requests
from api.services.paper_parser import parse_paper_from_url

# A minimal, valid PDF content containing the text "Hello World"
FAKE_PDF_CONTENT = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 4 0 R >> >> /MediaBox [0 0 612 792] /Contents 5 0 R >>
endobj
4 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
5 0 obj
<< /Length 44 >>
stream
BT
/F1 24 Tf
100 700 Td
(Hello World) Tj
ET
endstream
endobj
xref
0 6
0000000000 65535 f
0000000010 00000 n
0000000058 00000 n
0000000113 00000 n
0000000252 00000 n
0000000319 00000 n
trailer
<< /Size 6 /Root 1 0 R >>
startxref
415
%%EOF
"""

def test_parse_paper_from_url_success(mocker):
    """Tests successful fetching and parsing of a PDF from a URL."""
    # Mock the requests.get call
    mock_response = mocker.Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.content = FAKE_PDF_CONTENT
    mocker.patch('requests.get', return_value=mock_response)

    result = parse_paper_from_url('http://fakeurl.com/paper.pdf')

    assert result['success'] is True
    assert 'Hello World' in result['text_content']

def test_parse_paper_from_url_network_error(mocker):
    """Tests handling of a network error when fetching the PDF."""
    mocker.patch('requests.get', side_effect=requests.exceptions.RequestException('Network Error'))

    result = parse_paper_from_url('http://fakeurl.com/paper.pdf')

    assert 'error' in result
    assert 'Failed to fetch paper' in result['error']

def test_parse_paper_from_url_invalid_pdf(mocker):
    """Tests handling of invalid PDF content."""
    mock_response = mocker.Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.content = b"this is not a pdf"
    mocker.patch('requests.get', return_value=mock_response)

    result = parse_paper_from_url('http://fakeurl.com/paper.pdf')

    assert 'error' in result
    assert 'Failed to parse PDF' in result['error']
