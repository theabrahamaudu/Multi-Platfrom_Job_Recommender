from fastapi import FastAPI
import uvicorn
from etl.databases.routes.admin import admin
from etl.databases.cassandra.routes.user import user
from etl.databases.cassandra.routes.search import search
from etl.databases.cassandra.routes.clicks import clicks
from etl.databases.cassandra.routes.job import jobs
from etl.databases.chroma.routes.job_index import job_index
from src.utils.backend_log_config import backend as logger

app = FastAPI()
app.include_router(admin)
app.include_router(user)
app.include_router(jobs)
app.include_router(search)
app.include_router(clicks)
app.include_router(job_index)

if __name__ == "__main__":
    logger.info("Starting server...")
    uvicorn.run(app="app:app", host="0.0.0.0", port=28000, reload=True)
