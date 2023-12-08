"""
This module contains routes for the job embeddings index.
"""

from fastapi import APIRouter
from etl.databases.chroma.chroma_conn import ChromaConn
from etl.transform.vectorizer import vectorize
from etl.utils.utilities import get_user_metadata
from uuid import UUID
from src.utils.backend_log_config import backend as logger

# create router
job_index = APIRouter()
# connect to Chroma
conn = ChromaConn()
# Load job embeddings table
jobs_table = conn.session.get_collection(
            name=conn.collection_name,
            embedding_function=conn.embedding_function
        )


@job_index.get("/index/search/{user_id}&&{query}",
               response_model=list[str], tags=["Index"])
async def search_index(query: str, user_id: UUID):
    # fetch user metadata
    user_metadata = get_user_metadata(user_id)
    # create compisite query using user metadata and query
    composite_query = f"{query}, {user_metadata}"
    # search vector index with vectorised query
    # and return top 10 results
    query_vector = vectorize(composite_query)
    results = jobs_table.query(
        query_embeddings=query_vector,
        n_results=10
    )
    logger.info(f"Retrieved vector search results from Chroma."
                f"User ID: {user_id}")
    # parse and return results
    return results["ids"][0]
