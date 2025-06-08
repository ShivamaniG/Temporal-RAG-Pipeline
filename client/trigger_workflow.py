import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import asyncio
from temporalio.client import Client
from workflows.main_workflow import DocIngestionWorkflow
import uuid

async def main():
    client = await Client.connect("localhost:7233")
    unique_id = f"workflow-{uuid.uuid4()}"

    # Pass workflow arguments as a tuple
    result = await client.start_workflow(
        DocIngestionWorkflow.run,
        args=("id1", "https://arxiv.org/pdf/2501.08266"),
        id=unique_id,
        task_queue="doc-task-queue",
    )

    print("Workflow result:", await result.result())

if __name__ == "__main__":
    asyncio.run(main())
