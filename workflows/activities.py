import os
from temporalio import activity
import aiohttp
from unstructured.partition.auto import partition
from tempfile import NamedTemporaryFile
from google import genai
from google.genai import types
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
load_dotenv()

@activity.defn
async def fetch_document(file_url: str) -> bytes:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(file_url) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch file: {response.status}")
                return await response.read()
            
    except Exception as e:
        raise RuntimeError(f"Download failed: {str(e)}")
    
@activity.defn
async def parse_document(file_bytes: bytes, file_name: str) -> list[str]:
    suffix = os.path.splitext(file_name)[1]
    tmp_path = None
    try:
        with NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(file_bytes)
            tmp_file.flush()
            tmp_path = tmp_file.name  

        elements = partition(filename=tmp_path)

        chunks = [str(el) for el in elements if str(el).strip()]
        return chunks

    except Exception as e:
        raise RuntimeError(f"Failed to parse document: {str(e)}")

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

model = SentenceTransformer('all-MiniLM-L6-v2')
@activity.defn
async def generate_embeddings(text_chunks: list[str]) -> list[list[float]]:
    embeddings = model.encode(text_chunks, convert_to_tensor=False)
    return embeddings.tolist()

from pymilvus import connections, utility, FieldSchema, CollectionSchema, Collection, DataType

@activity.defn
async def store_embeddings(file_id: str, chunks: list[str], embeddings: list[list[float]]) -> str:
    if not chunks or not embeddings:
        raise ValueError(f"No chunks ({len(chunks)}) or embeddings ({len(embeddings)}) received for File ID: {file_id}")

    connections.connect(alias="default", host="localhost", port="19530")

    collection_name = "doc_chunks"

    try:
        embedding_dim = len(embeddings[0])
    except IndexError:
        raise ValueError("Embeddings list is empty or malformed.")

    if not utility.has_collection(collection_name):
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),  # Primary key
            FieldSchema(name="file_id", dtype=DataType.VARCHAR, max_length=256),          # Store file_id as string
            FieldSchema(name="chunk_index", dtype=DataType.INT64),                        # Index of chunk
            FieldSchema(name="chunk_text", dtype=DataType.VARCHAR, max_length=65535),     # Store text chunk
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=embedding_dim) # Embedding vector
        ]
        schema = CollectionSchema(fields=fields, description="Document Chunks")
        collection = Collection(name=collection_name, schema=schema)
        collection.create_index("embedding", {
            "index_type": "IVF_FLAT",
            "metric_type": "L2",
            "params": {"nlist": 128}
        })
        collection.load()
    else:
        collection = Collection(name=collection_name)

    if len(chunks) != len(embeddings):
        raise ValueError(f"Mismatch between chunks ({len(chunks)}) and embeddings ({len(embeddings)}).")

    chunk_indices = list(range(len(chunks)))
    file_ids = [file_id] * len(chunks)

    # Insert expects list of columns, where each column is a list of values
    data = [
        # 'id' is auto generated, so no need to pass here
        file_ids,
        chunk_indices,
        chunks,
        embeddings
    ]

    collection.insert(data)
    collection.flush()

    return f"Stored {len(chunks)} chunks with embeddings for File ID: {file_id}"
