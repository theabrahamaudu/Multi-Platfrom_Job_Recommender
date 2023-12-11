from multiprocessing import Process
from fastapi import APIRouter
from fastapi.responses import JSONResponse
import yaml
from etl.databases.cassandra.cassandra_conn import CassandraConn
from etl.databases.chroma.chroma_conn import ChromaConn
from etl.databases.cassandra.setup_db import SetupDB as CassandraSetupDB
from etl.databases.chroma.setup_db import SetupDB as ChromaSetupDB
from src.utils.backend_log_config import backend as logger
# scraping imports
from etl.extract.site_scraper import (
    IndeedScraper, LinkedinScraper, JobbermanScraper, scrape_with_retry
)
from etl.load.load_chroma import ChromaIO
from etl.load.load_cassandra import CassandraIO

# load config file
with open("./config/config.yaml", "r") as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        logger.error("Error loading config file: %s", exc)

admin = APIRouter()


@admin.get("/cassandra", tags=["Database Admin"])
async def initialize_cassandra():
    keyspace = config["database"]["cassandra"]["keyspace"]  # type: ignore
    if CassandraConn().session.keyspace == keyspace:
        logger.info("Cassandra status check passed")
        return JSONResponse(
            status_code=409,
            content={"message": "Cassandra already initialized"}
        )
    else:
        setup_db = CassandraSetupDB()
        setup_db.clean_keyspace()
        setup_db.setup_keyspace()
        assert CassandraConn().session.keyspace == keyspace
        logger.info(
            "Cassandra status check failed: Initialized new keyspace - %s",
            keyspace
        )
        return JSONResponse(
            status_code=200,
            content={"message": "Cassandra initialized"}
        )


@admin.get("/chroma", tags=["Database Admin"])
async def initialize_chroma():
    collection = config["database"]["chroma"]["collection"]  # type: ignore
    try:
        assert ChromaConn().session.list_collections()[0].name == collection
        logger.info("Chroma status check passed")
        return JSONResponse(
            status_code=409,
            content={"message": "Chroma already initialized"}
        )
    except Exception as e:
        logger.warning("Chroma status check failed: %s", e)
        setup_db = ChromaSetupDB()
        setup_db.clean_database()
        setup_db.setup_database()
        if ChromaConn().session.list_collections()[0].name == collection:
            logger.info(
                "Initialized new Chroma collection - %s",
                collection
            )
            return JSONResponse(
                status_code=200,
                content={"message": "Chroma initialized"}
            )
        else:
            return JSONResponse(
                status_code=500,
                content={"message": "Error initializing Chroma"}
            )


def scraping_pipeline():
    # Scrape Job and save to Cassandra
    scrape_with_retry(IndeedScraper)
    scrape_with_retry(JobbermanScraper)
    scrape_with_retry(LinkedinScraper)

    # Update Job embeddings in Chroma
    chroma_io = ChromaIO()
    chroma_io.load_from_cassandra()

    # Scrub older jobs and embeddings
    cassandra_io = CassandraIO()
    cassandra_io.scrub_jobs()
    chroma_io.scrub_jobs()


@admin.get("/scrape_jobs", tags=["Database Admin"])
async def scrape_jobs():
    try:
        scraping = Process(target=scraping_pipeline)
        scraping.start()
        logger.info("Scraping pipeline started")
        return JSONResponse(
            status_code=200,
            content={"message": "Scraping pipeline started"}
        )
    except Exception as e:
        logger.error("Error scraping jobs: %s", e)
        return JSONResponse(
            status_code=500,
            content={"message": "Error scraping jobs"}
        )


@admin.get("/user_count", tags=["Database Admin"])
async def get_users_count():
    try:
        user_count = CassandraConn().session.execute(
            "SELECT count(*) FROM users"
        )
        logger.info("Read user count from `users` table")
        return JSONResponse(
            status_code=200,
            content={"count": user_count.one()['count']}
        )
    except Exception as e:
        logger.error("Error getting user count: %s", e)
        return JSONResponse(
            status_code=500,
            content={"message": "Error getting user count"}
        )


@admin.get("/job_count", tags=["Database Admin"])
async def get_jobs_count():
    try:
        job_count = CassandraConn().session.execute(
            "SELECT count(*) FROM job_listings"
        )
        logger.info("Read job count from `job_listings` table")
        return JSONResponse(
            status_code=200,
            content={"count": job_count.one()['count']}
        )
    except Exception as e:
        logger.error("Error getting job count: %s", e)
        return JSONResponse(
            status_code=500,
            content={"message": "Error getting job count"}
        )
