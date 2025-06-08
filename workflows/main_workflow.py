from temporalio import workflow
import datetime

@workflow.defn
class DocIngestionWorkflow:
    @workflow.run
    async def run(self, file_id: str, file_url: str) -> str:
        content = await workflow.execute_activity(
            "fetch_document",
            args=(file_url,),
            schedule_to_close_timeout=datetime.timedelta(seconds=60),
        )
        chunks = await workflow.execute_activity(
            "parse_document",
            args=(content, file_url),
            schedule_to_close_timeout=datetime.timedelta(seconds=60),
        )
        embeddings = await workflow.execute_activity(
            "generate_embeddings",
            args=(chunks,),  
            schedule_to_close_timeout=datetime.timedelta(seconds=120),
        )
        await workflow.execute_activity(
            "store_embeddings",
            args=(file_id, chunks, embeddings),
            schedule_to_close_timeout=datetime.timedelta(seconds=120),
        )

        return f"✅ File ID: {file_id}, processed {len(chunks)} chunks with embeddings and stored in Milvus."

