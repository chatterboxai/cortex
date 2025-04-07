from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.schema import Document
import os

from app.services.rag.vectorstore import VectorStoreService

chatbot_id = '111b2d67-34fb-49ec-805d-537600b25d3c'

vector_store = VectorStoreService.get_vector_store(chatbot_id, 3072)

pipeline = IngestionPipeline(
    transformations=[
        MarkdownNodeParser(),
        OpenAIEmbedding(api_key=os.getenv("OPENAI_API_KEY"), model="text-embedding-3-large", dimensions=3072)
    ],
    vector_store=vector_store
)


document = Document(text="""## Why do we need to index documents?

Indexing documents is a process that allows us to store and retrieve information from a document. It is a way to make the document more searchable and easier to use.

### What is indexing?

""")
nodes = pipeline.run(documents=[document])
