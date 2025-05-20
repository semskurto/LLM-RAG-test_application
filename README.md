# Document Query System using RAG and LLMs

This application allows users to query information from documents found at specified URLs. It leverages a Retrieval Augmented Generation (RAG) approach with Large Language Models (LLMs) to provide answers based on the document's content. It's designed to quickly extract relevant information and generate concise answers from online documents.

## Key Features
* **URL-based document querying:** Users can specify a URL to a document, and the application will fetch and process its content.
* **LLM-powered answer generation:** Provides concise, context-aware answers to user queries based on the document's information.
* **Display of relevant text snippets:** Shows the most relevant sections from the source document that support the generated answer.
* **Easy local deployment via Docker:** The application can be easily set up and run in a local environment using Docker containers.

## Project Structure
A brief overview of the key files and directories in the project:
```
├── Dockerfile           # Defines the Docker image for the application.
├── main.py              # Main FastAPI application logic, including API endpoints.
├── model.py             # Handles LLM and embedding model interactions (loading, inference).
├── database_tools.py    # Manages Pinecone database operations (connection, querying, storage).
├── requirements.txt     # Lists Python dependencies for the project.
├── toolkit.py           # Contains utility functions or helper classes.
└── README.md            # This file, providing information about the project.
```

## Technical Stack
* **Embedding Model:** BAAI/bge-small-en (Generates vector embeddings from the document content for semantic search.)
* **Vector Database:** Pinecone (Stores document embeddings for efficient similarity searches and retrieval.)
* **LLM Model:** google/flan-t5-base (Generates human-readable answers based on the retrieved context from the documents.)
* **Deployment Framework:** FastAPI (Serves the application and exposes the querying API endpoint.)
* **Containerization:** Docker (Allows for easy local deployment and consistent runtime environment.)

## Limitations
* **Language Support:** Currently, the application only supports processing and querying documents in English.
* **Deployment Environment:** The application is configured for local deployment using Docker and has not been deployed to a cloud environment. This is due to time constraints during the initial development.

## Prerequisites

Before you begin, ensure you have the following:

*   **Docker:** Docker must be installed on your system. See [Docker's official website](https://docs.docker.com/get-docker/) for installation instructions.
*   **Pinecone Account:** You will need a Pinecone account and your API key and environment name to configure the application. See the section below on "Important: Configuring Pinecone Credentials".
*   **Hugging Face Token (Generally Recommended, but Optional for Basic Use):**
    The models used in this application (`BAAI/bge-small-en`, `google/flan-t5-base`) are downloaded from the Hugging Face Hub. While the application code does not strictly require a Hugging Face Token (`HF_TOKEN`) for these public models, setting `HF_TOKEN` as an environment variable in your system is a general good practice. It can help prevent potential download rate limits from the Hub and is essential if you plan to use private models or other advanced Hugging Face Hub features. For the basic functionality of this application as-is, you likely do not need to set this variable unless you encounter download issues. If you have `HF_TOKEN` set globally in your environment, the `transformers` library used by this application may automatically pick it up.
    *   Ensure you are in the root directory of the project (where `main.py`, `Dockerfile`, `requirements.txt`, etc., are located) before running deployment commands.

## Important: Configuring Pinecone Credentials

To use this application, you **must** manually configure your Pinecone API key and environment directly in the source code.

1.  Open the file: `database_tools.py`.
2.  Locate the `PineconeManager` class.
3.  Inside the `__init__` method, you will find the following lines:
    ```python
    self.api_key = "YOUR_PINECONE_API_KEY_HERE"
    self.environment = "YOUR_PINECONE_ENVIRONMENT_HERE"
    ```
4.  Replace `"YOUR_PINECONE_API_KEY_HERE"` with your actual Pinecone API key.
5.  Replace `"YOUR_PINECONE_ENVIRONMENT_HERE"` with your actual Pinecone environment name, which typically refers to the cloud provider (e.g., "aws", "gcp", "azure") for serverless indexes. The region is configured separately in the `PineconeManager` if needed (default is `us-east-1`).

**Failure to update these values will result in errors when the application tries to connect to Pinecone.**

## Deployment with Docker

Follow these steps to deploy and run the application using Docker:

1.  **Build the Docker Image:**
    This command builds a Docker image named `fastapi-app` from the `Dockerfile` in the current directory. The `.` indicates the current directory as the build context.
    ```shell
    docker build -t fastapi-app .
    ```

2.  **Run the Docker Container:**
    This command starts a Docker container from the `fastapi-app` image.
    ```shell
    docker run -d --name fastapi-container -p 8000:8000 fastapi-app
    ```
    **Note:** Ensure you have configured your Pinecone credentials in `database_tools.py` as described above before building and running the Docker image.
    *   `-d`: Runs the container in detached mode (in the background).
    *   `--name fastapi-container`: Assigns the name `fastapi-container` to the running container for easier management.
    *   `-p 8000:8000`: Maps port 8000 of your local machine (host) to port 8000 inside the container. This allows you to access the application via `localhost:8000`.
    *   `fastapi-app`: Specifies the Docker image to use for creating the container.

3.  **Check Container Logs (Optional):**
    To view the logs from the running container, which can be helpful for debugging or monitoring, use the following command:
    ```shell
    docker logs fastapi-container
    ```

### Verifying the Application

Once the container is running, you can verify that the application is operational:

1.  **Access the Root Endpoint:**
    Open your web browser and navigate to `http://localhost:8000` or `http://127.0.0.1:8000`.

2.  **Expected Output:**
    You should see a JSON response like `{"message":"Hello World"}`. This indicates that the FastAPI application is running correctly. (Note: The actual message might vary if the root endpoint's response has been customized).

3.  **Query Endpoint:**
    The main functionality for querying documents is available at the `http://localhost:8000/query/` endpoint. This endpoint expects POST requests with a JSON payload containing the `url` of the document and the `query`.

## Usage Examples

To interact with the application and query documents, you will send `POST` requests to the `/query/` endpoint.

**Endpoint:** `http://localhost:8000/query/`
**Method:** `POST`
**Request Body:** JSON object with the following parameters:
*   `url`: (string) The public URL of the document (e.g., PDF, text) to be processed and queried.
*   `query`: (string) The question you want to ask about the document's content.

**Successful Response:** The API will return a JSON object containing the generated answer and the 5 most relevant excerpts from the document that support the answer.

Below are a few examples using `curl` to interact with the API:

**Example 1: Querying a recent research paper on arXiv.**
This example asks for the main topic of a document hosted on arXiv.
```shell
 curl -X POST "http://localhost:8000/query/" -H "Content-Type: application/json" -d '{
  "url": "https://arxiv.org/pdf/2408.07666",
  "query": "What is the main topic of the document?"
}'
```

**Example 2: Asking about specific information in a NASA PDF document.**
This example queries a NASA document to find information about the "Lunar Mapping and Modeling Portal".
```shell
 curl -X POST "http://localhost:8000/query/" -H "Content-Type: application/json" -d '{
  "url": "https://eospso.nasa.gov/sites/default/files/publications/NASA%20Science%20Resources.pdf",
  "query": "What is Lunar Mapping and Modeling Portal?"
}'
```

**Example 3: Extracting historical details from a NASA history document.**
This example asks about major NASA projects from its first twenty years, based on a historical PDF.
```shell
 curl -X POST "http://localhost:8000/query/" -H "Content-Type: application/json" -d '{
  "url": "https://ajed.assembly.ca.gov/sites/ajed.assembly.ca.gov/files/Brief%20History%20of%20NASA.pdf",
  "query": "What are some of the example major project NASA has accomplished in its first twenty years?"
}'
```

## Future Enhancements

The following are potential areas for future development and improvement of this application:

*   **Model Upgrades and Optimization:** Investigate and integrate more recent LLMs and embedding models to potentially improve accuracy and performance. Explore libraries like vLLM for optimized inference, especially with larger models, to enhance efficiency and reduce computational costs.
*   **Enhanced API Security:** Enhance API security by implementing robust authentication and authorization mechanisms. Improve the management of sensitive information, such as API keys, by using environment variables or dedicated secrets management tools.
*   **Pinecone Namespace Strategy:** Re-evaluate the Pinecone namespace strategy. Depending on the intended use case (e.g., multi-tenancy, per-user data), consider alternative approaches such as using metadata and filtering within a single index, or dynamically managing namespaces.
*   **Expanded Document Format Support:** Add support for a wider range of document formats beyond PDF and plain text, such as DOCX, HTML, etc.
*   **Improved Error Handling and Logging:** Implement more comprehensive error handling and provide more detailed logging for easier debugging and monitoring.
*   **Cloud Deployment Options:** Develop configurations and scripts for deployment to cloud platforms (e.g., AWS, GCP, Azure) to provide scalability and wider accessibility.
*   **User Interface:** Create a simple web-based user interface (UI) to allow users to interact with the application without needing to use `curl` or other API tools.

## Contributing

Contributions are welcome! If you have suggestions for improvements, identify any bugs, or would like to contribute new features, please feel free to:
1.  Open an issue to discuss the change or bug.
2.  Fork the repository and create a new branch for your changes.
3.  Submit a pull request with a clear description of your contributions.

We appreciate your help in making this project better!

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
