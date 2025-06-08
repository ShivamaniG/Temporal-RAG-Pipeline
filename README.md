# Temporal-RAG-Pipeline

This project implements an end-to-end document ingestion pipeline using Temporal.io, Python asyncio, OpenAI embeddings, Unstructured.io for document parsing, and Milvus as the vector database. It simulates a real-world use case in Retrieval-Augmented Generation (RAG) systems, where documents are broken into chunks, embedded, and stored for efficient semantic search and retrieval.

### Documentation
For a detailed explanation of this project, along with screenshots demonstrating the workflow and successful execution, please refer to the documentation available here:
[Project Documentation](https://docs.google.com/document/d/1pb3_PnLo2wFXpGtc8STgqtOBxIN5NE_45MD94ysJHYw/edit?usp=sharing).
Additionally, the README.md file contains the major points about the project and detailed instructions on how to set up and run the application.


---

## 🚀 Project Objective

To automate the ingestion of documents (PDF, DOCX, XLSX, etc.) by:
- Downloading the file from a URL
- Parsing the content using [`unstructured.io`](https://www.unstructured.io) 
- Generating embeddings using the [all-MiniLM-L6-v2 embedding model](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) from Hugging Face.
- Storing both chunks and embeddings in [Milvus](https://milvus.io/) vector database.
- Managing the pipeline through [Temporal.io](https://temporal.io/) using asynchronous Python workers.

---

## 📦 Technologies Used

| Component        | Tool/Library                |
|------------------|-----------------------------|
| Workflow Engine | [Temporal.io](https://temporal.io) |
| Async Workers    | `temporalio[async]` SDK in Python |
| Document Parsing | [Unstructured.io](https://github.com/Unstructured-IO/unstructured) |
| Embedding Model  | Sentence Transformers |
| Vector Database  | [Milvus](https://milvus.io) using `pymilvus` |
| Deployment       | Docker Compose for Temporal & Milvus setup |

---

## 📁 Folder Structure

```
.
├── client/                # Workflow trigger script
├── worker/                # Executes tasks in workflow/
├── workflow/              # Temporal workflow and activities
├── milvus/                # Endpoints for Milvus Testing
├── docker-compose/        # Docker setup for Temporal & Milvus
├── requirements.txt       # Python dependencies
├── .gitignore             # Git ignore rules
└── README.md              # You're here

````

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/Temporal-RAG-Pipeline.git
cd Temporal-RAG-Pipeline
````

### 2. Set Up the Environment

```bash
python -m venv env
source env/bin/activate      # On Windows: env\Scripts\activate
pip install -r requirements.txt
```

### 3. Start Temporal & Milvus using Docker Compose

```bash
cd docker-compose
docker-compose up -d
```

Ensure that the following services are running:

* Temporal Web ([http://localhost:8233](http://localhost:8233))
* Milvus ([http://localhost:19530](http://localhost:19530))

### 4. Run the Temporal Worker

```bash
cd worker
python run_worker.py
```

### 5. Trigger the Workflow

```bash
cd client
python trigger_workflow.py
```

You’ll need to pass:

* `file_id` — any unique ID
* `file_url` — public URL of `.pdf`, `.docx`, `.xlsx`, etc.

---

## 🧠 How It Works (Workflow Steps)

1. **Trigger**: A workflow is triggered with `file_id` and `file_url`.
2. **Fetch File**: The file is downloaded from the provided URL.
3. **Parse File**: Unstructured.io parses the file into readable text chunks.
4. **Generate Embeddings**: Each chunk is passed to OpenAI to generate vector embeddings.
5. **Store in Milvus**: Embeddings + chunks + metadata are inserted into a Milvus collection.
6. **Complete**: Workflow marks successful ingestion of the document.

---

## 🧵 Milvus Schema

* **id:** Auto-generated unique record ID.
* **file\_id:** Text (up to 100 chars) identifying the source file.
* **chunk\_index:** Order of the chunk within the file.
* **chunk:** Text content of the document chunk.
* **embedding:** Vector of 768 numbers representing the chunk for similarity search.

### Check Milvus Schema

Run `milvus_test_point.py` in the `milvus` folder to connect to Milvus and print the collection schema.
```bash
python milvus/milvus_test_point.py
```
---

## 🔁 Asyncio Concurrency

The project leverages `asyncio` to enable concurrent processing of multiple chunks. This approach allows parallel OpenAI API requests for embedding generation, batched inserts into Milvus, and non-blocking file parsing and network I/O. By efficiently handling these I/O-bound tasks asynchronously, the solution keeps Temporal workers highly responsive and scalable.

---

## 📸 Example Output

```
✅ File ID: id1, processed 170 chunks with embeddings and stored in Milvus.
```

Check Temporal UI: [http://localhost:8233](http://localhost:8233)
Check Milvus insert log for confirmation.

---

## 🧪 Supported File Types

* `.pdf`
* `.docx`
* `.doc`
* `.xlsx`
* `.xls`

---

## 🙋‍♂️ Author

Shivamani G
Email: [shivamanigangarapu@gmail.com](mailto:shivamanigangarapu@gmail.com)
LinkedIn: [Shivamani G](https://www.linkedin.com/in/shivamanigangarapu/)

```
