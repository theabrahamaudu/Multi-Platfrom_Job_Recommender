from fastapi import FastAPI
import uvicorn
from backend.etl.databases.cassandra.routes.user import user
from backend.etl.databases.cassandra.routes.search import search
from backend.etl.databases.cassandra.routes.clicks import clicks
from backend.etl.databases.cassandra.routes.job import jobs
from backend.etl.databases.milvus.routes.job_index import job_index

app = FastAPI()
app.include_router(user)
app.include_router(jobs)
app.include_router(search)
app.include_router(clicks)
app.include_router(job_index)

if __name__ == "__main__":

    uvicorn.run(app="app:app", host="0.0.0.0", port=28000, reload=True)
