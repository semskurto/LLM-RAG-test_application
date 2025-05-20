import torch
from transformers import AutoTokenizer, AutoModel
import pinecone
from typing import List, Tuple


# Initialize huggingface embedding model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-small-en")
model = AutoModel.from_pretrained("BAAI/bge-small-en")

def get_embedding(text: str):
    """
    Generates an embedding vector for the given text using a pre-trained transformer model.

    :param text: The input text to be converted into an embedding.
    :type text: str
    :return: A numpy array representing the embedding of the input text.
    :rtype: numpy.ndarray

    The function tokenizes the input text and feeds it into the model. 
    The output embeddings are obtained from the last hidden state of the model and averaged across the sequence length. 
    The resulting vector is detached from the computation graph and returned as a numpy array.
    """
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).detach().numpy()



class PineconeManager:
    def __init__(self, index_name: str, dimension: int = 384, metric: str = 'cosine', region: str = 'us-east-1'):
        """
        Initializes the PineconeManager with necessary configurations.
        Pinecone API key and environment are set to hardcoded placeholders.

        :param index_name: The name of the index to be created or accessed.
        :param dimension: The dimension of the embeddings used in the index.
        :param metric: The similarity metric to be used ('cosine', 'dotproduct', etc.). Default is 'cosine'.
        :param region: The region where the index is hosted. Default is 'us-east-1'.
        """
        self.api_key = "YOUR_PINECONE_API_KEY_HERE"  # Hardcoded placeholder
        self.environment = "YOUR_PINECONE_ENVIRONMENT_HERE"  # Hardcoded placeholder, e.g., "aws", "gcp", "azure"

        self.index_name = index_name
        self.dimension = dimension
        self.metric = metric
        self.region = region
        
        self.pc = pinecone.Pinecone(api_key=self.api_key)
        # The 'environment' variable should represent the cloud provider (e.g., 'aws', 'gcp').
        # The region parameter for ServerlessSpec is separate.
        self.spec = pinecone.ServerlessSpec(cloud=self.environment, region=self.region)
        self.index = None

        self._initialize_index()

    def _initialize_index(self):
        """Initializes the Pinecone index. If the index does not exist, it creates one."""
        index_dict = self.pc.list_indexes()
        if self.index_name not in [index['name'] for index in index_dict]:
            self.pc.create_index(
                name=self.index_name,
                dimension=self.dimension,
                metric=self.metric,
                spec=self.spec
            )
        self.index = self.pc.Index(self.index_name)

    def upsert_embeddings(self, chunks: List[str], namespace: str = ""):
        """
        Inserts embeddings into the Pinecone index.

        :param chunks: A list of text chunks to be embedded and inserted.
        :param namespace: The namespace under which the embeddings will be stored. Default is an empty string.
        """
        print(3)
        vectors = [(str(i), get_embedding(chunk)[0].tolist(), {'text': chunk}) for i, chunk in enumerate(chunks)]
        self.index.upsert(vectors=vectors, namespace=namespace)
        print("Embeddings have been successfully inserted into Pinecone.")

    def query_index(self, query: str, top_k: int = 5, namespace: str = "") -> List[dict]:
        """
        Queries the Pinecone index for the most relevant embeddings.

        :param query: The query string for which to search the index.
        :param top_k: The number of top results to return. Default is 5.
        :param namespace: The namespace from which to query embeddings. Default is an empty string.
        :return: A list of the most relevant embeddings, including metadata.
        """
        query_embedding = get_embedding(query).tolist()
        results = self.index.query(vector=query_embedding, top_k=top_k, includeValues=False, includeMetadata=True, namespace=namespace)
        return results["matches"]

    def describe_index(self):
        """
        Describes the current status and statistics of the Pinecone index.

        :return: A dictionary containing the index statistics.
        """
        return self.index.describe_index_stats()

    def list_indexes(self) -> List[str]:
        """
        Lists all available indexes in Pinecone.

        :return: A list of index names.
        """
        index_dict = self.pc.list_indexes()
        return [index['name'] for index in index_dict]
    
    def list_namespaces(self):
        """
        Lists all the namespaces in the current Pinecone index.
        
        :return: A list of all namespaces in the index.
        :rtype: list of str
        """
        # Pinecone currently doesn't have a direct API to list all namespaces, 
        # so we'll simulate this by querying index statistics which often include namespaces.
        stats = self.index.describe_index_stats()
        return list(stats.get('namespaces', {}).keys())
