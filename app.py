from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from toolkit import split_pdf_chunks, download_pdf_and_checksum
from database_tools import PineconeManager, get_embedding
from model import AnswerGenerator

app = FastAPI()

# Initialize Pinecone with API key and environment settings
pcdb = PineconeManager(index_name="test_case_glov", metric='cosine')

# Initialize LLM Model for query answer
answer_generator = AnswerGenerator()

class QueryRequest(BaseModel):
    url: str  # The URL of the PDF to be processed
    query: str  # The query string to search within the PDF


def perform_embedding_and_indexing(url: str):
    """
    Downloads a PDF, splits it into chunks, and upserts the embeddings into Pinecone.

    Parameters:
    url (str): The URL of the PDF to process.

    Returns:
    List[str]: The list of chunks from the PDF.
    """
    pdf_file, checksum =download_pdf_and_checksum(url)
    # Check if the PDF is already indexed namespaces, if not, index it
    pcdb_index_namespaces = pcdb.list_namespaces
    print(pcdb_index_namespaces)
    if checksum not in pcdb_index_namespaces:
        chunks = split_pdf_chunks(pdf_file)
        pcdb.upsert_embeddings(chunks, namespace=checksum)
    else:
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
    dict: A dictionary containing the generated answer.
    """
    _, checksum = perform_embedding_and_indexing(request.url)

    # Query Pinecone for the top 5 most relevant chunks
    results = pcdb.query_index(str(request.query), namespace=checksum)

    # Get the top 5 context chunks
    top_chunks = [match['metadata']['text'] for match in results['matches']]

    # Generate an answer based on the retrieved chunks
    answer = answer_generator.generate_answer(" ".join(top_chunks), request.query)

    return {
            'input':{
                "url": str(request.url),
                "query": str(request.query)
                },
            'output':{
                "answer": str(answer),
                "top_5_chunks": str(" ".join(top_chunks))
                }
            }
