from pymilvus import (
    connections,
    FieldSchema, CollectionSchema, DataType,
    Collection,
    utility
)
from sentence_transformers import SentenceTransformer

MILVUS_HOST = "localhost"
MILVUS_PORT = "19530"
COLLECTION_NAME = "doc_chunks"
EMBEDDING_DIM = 384  

embedder = SentenceTransformer('all-MiniLM-L6-v2')  

def connect_milvus():
    connections.connect(
        alias="default",
        host=MILVUS_HOST,
        port=MILVUS_PORT
    )
    print("Connected to Milvus")

def create_collection():
    if utility.has_collection(COLLECTION_NAME):
        print(f"Collection '{COLLECTION_NAME}' already exists")
        return Collection(COLLECTION_NAME)

    fields = [
        FieldSchema(name="file_id", dtype=DataType.VARCHAR, max_length=256, is_primary=False, description="File ID"),
        FieldSchema(name="chunk_index", dtype=DataType.INT64, is_primary=False, description="Chunk Index"),
        FieldSchema(name="chunk_text", dtype=DataType.VARCHAR, max_length=65535, is_primary=False, description="Chunk text"),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=EMBEDDING_DIM, description="Embedding vector") 
    ]

    schema = CollectionSchema(fields, description="Document chunks collection")
    collection = Collection(name=COLLECTION_NAME, schema=schema)

    index_params = {
        "metric_type": "L2",
        "index_type": "IVF_FLAT",
        "params": {"nlist": 128}
    }
    collection.create_index(field_name="embedding", index_params=index_params)
    print(f"Created collection '{COLLECTION_NAME}' with index")
    return collection

def generate_embeddings(chunks):
    # Generate embeddings for a list of chunks (texts)
    embeddings = embedder.encode(chunks, convert_to_numpy=True).tolist()
    return embeddings

def insert_chunks(collection: Collection, file_id: str, chunks: list):
    embeddings = generate_embeddings(chunks)
    assert len(chunks) == len(embeddings), "Chunks and embeddings length mismatch"

    file_ids = [file_id] * len(chunks)
    chunk_indices = list(range(len(chunks)))

    entities = [
        file_ids,
        chunk_indices,
        chunks,
        embeddings
    ]

    insert_result = collection.insert(entities)
    collection.flush()
    print(f"Inserted {len(chunks)} chunks for file_id={file_id}")
    return insert_result

def query_chunks_by_file(collection, file_id: str):
    expr = f'file_id == "{file_id}"'
    results = collection.query(expr=expr, output_fields=["chunk_text", "chunk_index", "embedding"])
    return results

if __name__ == "__main__":
    connect_milvus()
    collection = create_collection()

    # Example chunks to insert
    example_file_id = "id1"
    example_chunks = [
        "Deep learning improves disaster management.",
        "U-Net shows lowest validation loss but lower accuracy.",
        "ResNet balances accuracy and precision well.",
    ]

    insert_chunks(collection, example_file_id, example_chunks)

    stored_chunks = query_chunks_by_file(collection, example_file_id)
    print(f"Chunks stored for File ID '{example_file_id}':")
    for idx, chunk in enumerate(stored_chunks):
        print(f"{idx+1}. Chunk Index: {chunk['chunk_index']}")
        print(f"   Text: {chunk['chunk_text']}")
        print(f"   Embedding (first 5 values): {chunk['embedding'][:5]}")  # Print first 5 embedding values
