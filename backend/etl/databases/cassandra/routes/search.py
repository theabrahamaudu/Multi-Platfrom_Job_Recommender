from fastapi import APIRouter
from backend.etl.databases.cassandra.data_models import Search
from backend.etl.databases.cassandra.table_models import SearchMetadata


search = APIRouter()


@search.get("/search", tags=["Search"])
async def read_all_searches():
    return list(SearchMetadata.objects.all())


@search.get("/search/{user_id}", response_model=list[Search], tags=["Search"])
async def read_search(user_id: str):
    return list(
        SearchMetadata.objects(
            SearchMetadata.user_id == user_id
        )
    )


@search.post("/search", tags=["Search"])
async def write_search(search: Search):
    return SearchMetadata.objects.create(
        user_id=str(search.user_id),
        search_query=search.search_query,
        search_results=search.search_results
    )


@search.put("/search/{search_id}", response_model=Search, tags=["Search"])
async def update_search(search_id: str, search: Search):
    old_search = SearchMetadata.get(SearchMetadata.search_id == search_id)
    SearchMetadata.objects(
        search_id=old_search.search_id,
        search_timestamp=old_search.search_timestamp
    ).if_exists().update(
        search_query=search.search_query,
        search_results=search.search_results
    )
    return SearchMetadata.get(SearchMetadata.search_id == search_id)


@search.delete("/search/{id}", tags=["Search"])
async def delete_search(search_id: str):
    search = SearchMetadata.get(SearchMetadata.search_id == search_id)
    return SearchMetadata.objects(
        search_id=search_id,
        search_timestamp=search.search_timestamp
    ).if_exists().delete()
