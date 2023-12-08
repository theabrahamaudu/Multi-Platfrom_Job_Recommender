"""
This module contains CRUD routes for the `search_metadata` table in Cassandra.
"""

from fastapi import APIRouter
from etl.databases.cassandra.data_models import Search
from etl.databases.cassandra.table_models import SearchMetadata
from src.utils.backend_log_config import backend as logger

# create router
search = APIRouter()


@search.get("/search/read_all", tags=["Search"])
async def read_all_searches():
    """
    Retrieves all searches stored in the `search_metadata` table.

    Returns:
    - List[SearchMetadata]: A list of all searches.
    """
    all_searches = list(SearchMetadata.objects.all())
    logger.info(
        f"Read {len(all_searches)} searches from `search_metadata` table"
    )
    return all_searches


@search.get("/search/fetch/{user_id}",
            response_model=list[Search],
            tags=["Search"])
async def read_search(user_id: str):
    """
    Retrieves all search data for a specific user from the
    `search_metadata` table.

    Args:
    - user_id (str): The unique identifier of the user.

    Returns:
    - List[Search]: A list of search metadata related to the specified user.
    """
    search = list(
        SearchMetadata.objects(
            SearchMetadata.user_id == user_id
        )
    )
    logger.info(f"Read search for user {user_id}")
    return search


@search.post("/search/new", tags=["Search"])
async def write_search(search: Search):
    """
    Creates new search metadata for a user in the `search_metadata` table.

    Args:
    - search (Search): The search metadata to be added.

    Returns:
    - Search: The newly created search metadata.
    """
    search = SearchMetadata.objects.create(
        user_id=str(search.user_id),
        search_query=search.search_query,
        search_results=search.search_results
    )
    logger.info(f"Write search for user {search.user_id}")
    return search


@search.put("/search/update/{search_id}",
            response_model=Search,
            tags=["Search"])
async def update_search(search_id: str, search: Search):
    """
    Updates an existing search in the `search_metadata` table.

    Args:
    - search_id (str): The ID of the search to be updated.
    - search (Search): The updated search metadata.

    Returns:
    - Search: The updated search metadata.
    """
    # load existing search to ensure it exists
    old_search = SearchMetadata.get(SearchMetadata.search_id == search_id)
    # update search
    SearchMetadata.objects(
        search_id=old_search.search_id,
        search_timestamp=old_search.search_timestamp
    ).if_exists().update(
        search_query=search.search_query,
        search_results=search.search_results
    )
    logger.info(
        f"Updated query for user {search.user_id} and"
        f" search {search.search_id}"
    )
    return SearchMetadata.get(SearchMetadata.search_id == search_id)


@search.delete("/search/delete/{search_id}", tags=["Search"])
async def delete_search(search_id: str):
    """
    Deletes a specific search from the `search_metadata` table.

    Args:
    - search_id (str): The ID of the search to be deleted.

    Returns:
    - None: If the deletion is successful, no return value is provided.
    """
    # load existing search to ensure it exists
    search = SearchMetadata.get(SearchMetadata.search_id == search_id)

    # delete search
    deleted_search = SearchMetadata.objects(
        search_id=search_id,
        search_timestamp=search.search_timestamp
    ).if_exists().delete()
    logger.info(
        f"Delete search for user {search.user_id} and"
        f" search_id {search.search_id}"
    )
    return deleted_search
