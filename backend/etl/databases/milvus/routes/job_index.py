from fastapi import APIRouter
from pymilvus import Collection
from backend.etl.databases.milvus.milvus_conn import MilvusConn
from backend.etl.databases.milvus.table_models import collection_name
from backend.etl.transform.vectorizer import vectorize
from backend.etl.utils.utilities import get_user_metadata
from uuid import UUID


job_index = APIRouter()

conn = MilvusConn()

jobs_table = Collection(
    name=collection_name,
    using=conn.session_name,
)
jobs_table.load()


@job_index.get("/index/search/{user_id}&&{query}",
               response_model=list[str], tags=["Index"])
async def search_index(query: str, user_id: UUID):

    user_metadata = get_user_metadata(user_id)
    composite_query = f"{query}, {user_metadata}"
    query_vector = vectorize(composite_query).tolist()
    results = jobs_table.search(
        [query_vector],
        anns_field="embedding",
        param={"metric_type": "L2", "params": {"nprobe": 10}},
        consistency_level="Strong",
        limit=10
    )
    return results[0].ids  # type: ignore