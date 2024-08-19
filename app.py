from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import json
import time
from toolkit import split_pdf_chunks, download_pdf_and_checksum
from database_tools import PineconeManager
from model import AnswerGenerator

app = FastAPI()

# Initialize Pinecone with API key and environment settings
pcdb = PineconeManager(index_name="test-case-glov", metric='cosine')

# Initialize LLM Model for query answer
answer_generator = AnswerGenerator()


class QueryRequest(BaseModel):
    url: str  # The URL of the PDF to be processed
    query: str  # The query string to search within the PDF


def format_json(response):
    """
    Formats a JSON response for better readability.
    
    Parameters:
    response (dict or str): The JSON response to format. Can be a dictionary or a JSON string.

    Returns:
    str: A formatted JSON string.
    """

    response = json.loads(response)
    
    # Format the JSON with indentation and sorting keys
    return json.dumps(response, indent=4, sort_keys=True)


def check_namespaces(namespace: str) -> bool:
    """
    Checks if a namespace exists in Pinecone.

    Parameters:
    namespace (str): The namespace to check for existence.

    Returns:
    bool: True if the namespace exists, False otherwise.

    This function queries Pinecone to determine if a specified namespace already exists.
    It is used to avoid re-indexing PDF content that has already been processed.
    """
    # List all namespaces in Pinecone
    namespaces = pcdb.list_namespaces()
    
    # Check if the given namespace is in the list
    return namespace in namespaces


def perform_embedding_and_indexing(url: str):
    """
    Downloads a PDF, splits it into chunks, and upserts the embeddings into Pinecone.

    Parameters:
    url (str): The URL of the PDF to process.

    Returns:
    List[str]: The list(or None) of chunks from the PDF.
    """
    pdf_file, checksum = download_pdf_and_checksum(url)

    # Check if the PDF is already indexed namespaces, if not, index it
    if not check_namespaces(checksum):
        print(1)
        chunks = split_pdf_chunks(pdf_file)
        print(2)
        pcdb.upsert_embeddings(chunks, namespace=checksum)
        time.sleep(3)
    else:
        print(10000000000000000000000000)
        chunks = None
    return chunks, checksum


@app.post("/query/")
async def query_endpoint(request: QueryRequest):
    """
    Endpoint for querying a PDF document. If the PDF is not in the database, 
    it will be indexed first. Then, it searches for the most relevant chunks 
    and generates an answer.

    Parameters:
    request (QueryRequest): The request containing the PDF URL and the query string.

    Returns:
    dict: A dictionary containing the generated LLM answer and the top 5 chunks.
    """
    _, checksum = perform_embedding_and_indexing(request.url)

    # Query Pinecone for the top 5 most relevant chunks
    matches = pcdb.query_index(str(request.query), namespace=checksum)

    # Get the top 5 context chunks
    top_chunks = [match['metadata']['text'] for match in matches]

    # Generate an answer based on the retrieved chunks
    answer = answer_generator.generate_answer(" ".join(top_chunks), request.query)

    response = {"LLM answer": str(answer), "top_5_chunks": str("\n".join(top_chunks))}

    return json.dumps(response, indent=4)
