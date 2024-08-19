import PyPDF2
import requests
import hashlib
from io import BytesIO


def download_pdf_and_checksum(url: str):
    """
    Downloads a PDF from the provided URL and generates an MD5 checksum.

    :param url: The URL of the PDF document to be downloaded.
    :type url: str
    :return: A tuple containing the PDF content as a BytesIO object and an MD5 checksum of the PDF content.
    :rtype: tuple (BytesIO, str)

    This function downloads the PDF file and calculates an MD5 checksum to ensure data integrity.

    :raises HTTPException: If the request to download the PDF fails with a status code other than 200.
    """
    # Download the PDF file
    response = requests.get(url)
    
    # Check for request success
    if response.status_code != 200:
        raise requests.HTTPError(f"Failed to download PDF. HTTP Status Code: {response.status_code}")
    
    # Calculate an MD5 checksum for the PDF content
    checksum = hashlib.md5(response.content).hexdigest()
    
    # Load PDF content into memory
    pdf_file = BytesIO(response.content)
    
    return pdf_file, str(checksum)

def split_pdf_chunks(pdf_file: BytesIO, chunk_size: int = 100):
    """
    Splits the text content of a PDF file into smaller chunks of a specified size.

    :param pdf_file: The PDF content as a BytesIO object.
    :type pdf_file: BytesIO
    :param chunk_size: The number of words in each chunk. Default is 100 words per chunk.
    :type chunk_size: int, optional
    :return: A list of text chunks, each containing a specified number of words.
    :rtype: list of str

    The function reads the text content from each page of the PDF, combines the text,
    and then splits it into smaller chunks based on the specified chunk size.
    """
    # Process the PDF with PyPDF2
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()

    if not text:
        raise ValueError("No text could be extracted from the PDF.")

    # Split the text into chunks of the specified size
    words = text.split()
    chunks = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
    
    return chunks
    