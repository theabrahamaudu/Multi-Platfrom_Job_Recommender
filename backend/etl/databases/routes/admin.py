from multiprocessing import Process
from fastapi import APIRouter
"""
This module provides routes for managing the database as an admin
user from within the web application.
"""

from fastapi.responses import JSONResponse
import yaml
from etl.databases.cassandra.cassandra_conn import CassandraConn
from etl.databases.chroma.chroma_conn import ChromaConn
from etl.databases.cassandra.setup_db import SetupDB as CassandraSetupDB
from etl.databases.chroma.setup_db import SetupDB as ChromaSetupDB
from src.utils.backend_log_config import backend as logger
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

# create router
admin = APIRouter()


@admin.get("/cassandra", tags=["Database Admin"])
async def initialize_cassandra():
    """
    Initializes the Cassandra database by creating the keyspace if it does
    not already exist.

    Returns:
    - JSONResponse: A message indicating the status of the Cassandra
      initialization.

    This function checks if the specified keyspace for Cassandra already
    exists. If the keyspace exists, it returns a message indicating that
    Cassandra is already initialized. If not, it cleans any existing keyspace
    with the same name and sets up a new keyspace.
    Finally, it verifies the creation of the keyspace and returns the
    corresponding status message.
    """
    # load keyspace name
    keyspace = config["database"]["cassandra"]["keyspace"]  # type: ignore
    # check if keyspace already exists
    if CassandraConn().session.keyspace == keyspace:
        logger.info("Cassandra status check passed")
        return JSONResponse(
            status_code=409,
            content={"message": "Cassandra already initialized"}
        )
    # if not, create new keyspace
    else:
        setup_db = CassandraSetupDB()
        setup_db.clean_keyspace()
        setup_db.setup_keyspace()
        # check if keyspace was created
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
    """
    Initializes the Chroma database by creating the collection if it does not
    already exist.

    Returns:
    - JSONResponse: A message indicating the status of the Chroma
      initialization.

    This function checks if the specified collection for Chroma already exists.
    If the collection exists, it returns a message indicating that Chroma is
    already initialized. If not, it cleans any existing collection with the
    same name and sets up a new collection.
    Finally, it verifies the creation of the collection and returns the
    corresponding status message.
    """
    # load collection name
    collection = config["database"]["chroma"]["collection"]  # type: ignore
    try:
        # check if collection already exists
        assert ChromaConn().session.list_collections()[0].name == collection
        logger.info("Chroma status check passed")
        return JSONResponse(
            status_code=409,
            content={"message": "Chroma already initialized"}
        )
    except Exception as e:
        # if not, create new collection
        logger.warning("Chroma status check failed: %s", e)
        setup_db = ChromaSetupDB()
        setup_db.clean_database()
        setup_db.setup_database()
        # check if it was created
        if ChromaConn().session.list_collections()[0].name == collection:
            logger.info(
                "Initialized new Chroma collection - %s",
                collection
            )
            return JSONResponse(
                status_code=200,
                content={"message": "Chroma initialized"}
            )
        # if not, return error
        else:
            return JSONResponse(
                status_code=500,
                content={"message": "Error initializing Chroma"}
            )


def scraping_pipeline():
    """
    Runs the data scraping and cleanup pipeline.

    This function executes the following steps:
    1. Initiates scraping job data from different sources (Indeed, Jobberman,
       LinkedIn), saving the scraped jobs to Cassandra.
    2. Load jobs from Cassandra database, embed them and push them into Chroma.
    3. Scrubs older jobs and their corresponding embeddings from both
       Cassandra and Chroma.
    """

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
    """
    Starts the data scraping pipeline in a new process.

    Initiates the scraping process for job data from multiple sources.
    If successful, it starts the scraping pipeline in a separate process,
    logging the start of the pipeline and returning a success message.
    If an error occurs during the pipeline execution, it logs the error and
    returns an error message.
    """
    try:
        # call scraping pipeline in a new process
        scraping = Process(target=scraping_pipeline)
        scraping.start()
        logger.info("Scraping pipeline started")
        # let the admin know that the pipeline is running
        return JSONResponse(
            status_code=200,
            content={"message": "Scraping pipeline started"}
        )
    except Exception as e:
        # if error, let the admin know
        logger.error("Error scraping jobs: %s", e)
        return JSONResponse(
            status_code=500,
            content={"message": "Error scraping jobs"}
        )


@admin.get("/user_count", tags=["Database Admin"])
async def get_users_count():
    """
    Retrieves the total count of users from the Cassandra database.

    Queries the `users` table in the Cassandra database to obtain
    the count of users.
    If successful, returns the count as a JSON response.
    If an error occurs during the count retrieval, logs the error and
    returns an error message.
    """
    try:
        # get user count from cassandra database
        user_count = CassandraConn().session.execute(
            "SELECT count(*) FROM users"
        )
        logger.info("Read user count from `users` table")
        return JSONResponse(
            status_code=200,
            content={"count": user_count.one()['count']}
        )
    except Exception as e:
        # if error, let the admin know
        logger.error("Error getting user count: %s", e)
        return JSONResponse(
            status_code=500,
            content={"message": "Error getting user count"}
        )


@admin.get("/job_count", tags=["Database Admin"])
async def get_jobs_count():
    """
    Retrieves the total count of jobs from the Cassandra database.

    Queries the `job_listings` table in the Cassandra database to
    obtain the count of jobs.
    If successful, returns the count as a JSON response.
    If an error occurs during the count retrieval, logs the error and
    returns an error message.
    """
    try:
        # get job count from cassandra database
        job_count = CassandraConn().session.execute(
            "SELECT count(*) FROM job_listings"
        )
        logger.info("Read job count from `job_listings` table")
        return JSONResponse(
            status_code=200,
            content={"count": job_count.one()['count']}
        )
    except Exception as e:
        # if error, let the admin know
        logger.error("Error getting job count: %s", e)
        return JSONResponse(
            status_code=500,
            content={"message": "Error getting job count"}
        )
