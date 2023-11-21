from fastapi import FastAPI
import uvicorn
from backend.etl.databases.cassandra.routes.user import user
from backend.etl.databases.cassandra.routes.search import search

app = FastAPI()
app.include_router(user)
app.include_router(search)

if __name__ == "__main__":

    uvicorn.run(app="app:app", host="0.0.0.0", port=28000, reload=True)
