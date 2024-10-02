# LLM RAG Test Application
 
### Application features:
All the specified stages of the application have been completed.
The necessary search can be made with the url and query sent in the request, and a simple LLM model also produces short answers, the 5 most relevant parts obtained with the LLM answer and vector database are presented.

* **embedding model**: BAAI/bge-small-en
* **database**: pinecone
* **LLM model**: google/flan-t5-base
* **deployment**: Can be deployed locally in docker with FastAPI  

*Not deployed in the cloud environment due to time constraints.*

**Warnings:**
Only english language is supported.


## Deployment with Docker  
1. Create Docker Image:  
Make sure you are in the relevant directory. (There should be main.py, Dockerfile, requirement.txt and other files in the current directory)  
```shell
docker build -t fastapi-app .
``` 
2. Run Docker Cointainer  
```shell
docker run -d --name fastapi-container -p 8000:8000 fastapi-app
```

Also check docker logs:
```shell
docker logs fastapi-container
```

Access from your local machine (host machine):  
 http://localhost:8000 or http://127.0.0.1:8000  

 You can see that Fast API is working here, but the address we will send the request to is:  
 http://localhost:8000/query/  


 ## Test example:  
```shell
 curl -X POST "http://localhost:8000/query/" -H "Content-Type: application/json" -d '{
  "url": "https://arxiv.org/pdf/2408.07666",
  "query": "What is the main topic of the document?"
}'
```

```shell
 curl -X POST "http://localhost:8000/query/" -H "Content-Type: application/json" -d '{
  "url": "https://eospso.nasa.gov/sites/default/files/publications/NASA%20Science%20Resources.pdf",
  "query": "What is Lunar Mapping and Modeling Portal?"
}'
```

```shell
 curl -X POST "http://localhost:8000/query/" -H "Content-Type: application/json" -d '{
  "url": "https://ajed.assembly.ca.gov/sites/ajed.assembly.ca.gov/files/Brief%20History%20of%20NASA.pdf",
  "query": "What are some of the example major project NASA has accomplished in its first twenty years?"
}'
```  

# NEXT STEP...
More up-to-date models can be preferred. At the same time, it can be used with the vLLM library to solve the cost of up-to-date models, for performance and efficiency.

Current API security requirements should be reviewed and the necessary information should be stored more securely. (Exp.: api key management, ... )

Currently, different pdfs are saved on different name spaces on pinecone, this can be changed according to the usage situation.


