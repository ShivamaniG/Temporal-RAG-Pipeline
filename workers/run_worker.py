import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import asyncio
from temporalio.worker import Worker
from workflows.activities import fetch_document, parse_document, generate_embeddings, store_embeddings
from workflows.main_workflow import DocIngestionWorkflow  # placeholder for now
from temporalio.client import Client

async def main():
    client = await Client.connect("localhost:7233")

    worker = Worker(
        client,
        task_queue="doc-task-queue",
        workflows=[DocIngestionWorkflow],  # dummy for now
        activities=[fetch_document,parse_document,generate_embeddings,store_embeddings],
    )

    print("Worker started. Listening on 'doc-task-queue'...")
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
