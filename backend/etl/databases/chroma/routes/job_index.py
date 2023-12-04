from fastapi import APIRouter
from etl.databases.chroma.chroma_conn import ChromaConn
from etl.transform.vectorizer import vectorize
from etl.utils.utilities import get_user_metadata
from uuid import UUID


job_index = APIRouter()

conn = ChromaConn()

jobs_table = conn.session.get_collection(
            name=conn.collection_name,
            embedding_function=conn.embedding_function
        )


@job_index.get("/index/search/{user_id}&&{query}",
               response_model=list[str], tags=["Index"])
async def search_index(query: str, user_id: UUID):
    user_metadata = get_user_metadata(user_id)
    composite_query = f"{query}, {user_metadata}"
    query_vector = vectorize(composite_query)
    results = jobs_table.query(
        query_embeddings=query_vector,
        n_results=10
    )
    
    return results["ids"][0]
