"""
This module contains CRUD routes for the `job_listings` table in Cassandra.
"""
from fastapi import APIRouter
from etl.databases.cassandra.data_models import Job
from etl.databases.cassandra.table_models import JobListings
from src.utils.backend_log_config import backend as logger

# create router
jobs = APIRouter()


@jobs.get("/jobs/read_all", tags=["Jobs"])
async def read_all_jobs():
    """
    Retrieves all available job listings from the `job_listings` table.

    Returns:
    - list: A list containing all job listings retrieved from the database.
    """
    all_jobs = list(JobListings.objects.all())
    logger.info(f"Read {len(all_jobs)} jobs from `job_listings` table")
    return all_jobs


@jobs.get("/jobs/fetch/{job_id}",
          response_model=list[Job],
          tags=["Jobs"])
async def read_job(job_id: str):
    """
    Retrieves a specific job listing from the `job_listings`
    table based on the provided job ID.

    Args:
    - job_id (str): The unique identifier for the job listing to retrieve.

    Returns:
    - list: A list containing the job listing(s) retrieved based
      on the provided job ID.
    """
    job = list(
        JobListings.objects(
            JobListings.uuid == job_id
        )
    )
    logger.info(f"Read job {job_id} from `job_listings` table")
    return job


@jobs.post("/jobs/new", tags=["Jobs"])
async def write_job(job: Job):
    """
    Creates a new job listing in the `job_listings` table.

    Args:
    - job (Job): The job listing data to be added.

    Returns:
    - Job: The newly created job listing.
    """
    job = JobListings.objects.if_not_exists().create(
        uuid=str(job.uuid),
        skipped=job.skipped,
        scraped_at=job.scraped_at,
        source=job.source,
        job_id=job.job_id,
        job_title=job.job_title,
        company_name=job.company_name,
        location=job.location,
        date=job.date,
        job_link=job.job_link,
        job_desc=job.job_desc,
        seniority=job.seniority,
        emp_type=job.emp_type,
        job_func=job.job_func,
        ind=job.ind
    )
    logger.info(f"Write job {job.job_id} to `job_listings` table")
    return job


@jobs.put("/jobs/update/{job_id}",
          response_model=Job,
          tags=["Jobs"])
async def update_job(job_id: str, job: Job):
    """
    Updates an existing job listing in the `job_listings` table.

    Args:
    - job_id (str): The unique identifier of the job listing to be updated.
    - job (Job): The updated job listing data.

    Returns:
    - Job: The updated job listing after the changes have been applied.
    """
    JobListings.objects(
        uuid=job_id
    ).if_exists().update(
        skipped=job.skipped,
        scraped_at=job.scraped_at,
        source=job.source,
        job_id=job.job_id,
        job_title=job.job_title,
        company_name=job.company_name,
        location=job.location,
        date=job.date,
        job_link=job.job_link,
        job_desc=job.job_desc,
        seniority=job.seniority,
        emp_type=job.emp_type,
        job_func=job.job_func,
        ind=job.ind
    )
    job = JobListings.get(JobListings.uuid == job_id)
    logger.info(f"Updated job {job_id} in `job_listings` table")
    return job


@jobs.delete("/jobs/delete/{job_id}", tags=["Jobs"])
async def delete_job(job_id: str):
    """
    Deletes a job listing from the `job_listings` table.

    Args:
    - job_id (str): The unique identifier of the job listing to be deleted.

    Returns:
    - None: If the deletion is successful, no return value is provided.
    """
    job = JobListings.get(JobListings.uuid == job_id)
    deleted_job = JobListings.objects(
        uuid=job.uuid
    ).if_exists().delete()
    logger.info(f"Delete job {job_id} from `job_listings` table")
    return deleted_job
