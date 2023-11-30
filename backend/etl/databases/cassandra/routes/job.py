from fastapi import APIRouter
from etl.databases.cassandra.data_models import Job
from etl.databases.cassandra.table_models import JobListings


jobs = APIRouter()


@jobs.get("/jobs/read_all", tags=["Jobs"])
async def read_all_jobs():
    return list(JobListings.objects.all())


@jobs.get("/jobs/fetch/{job_id}",
          response_model=list[Job],
          tags=["Jobs"])
async def read_job(job_id: str):
    return list(
        JobListings.objects(
            JobListings.uuid == job_id
        )
    )


@jobs.post("/jobs/new", tags=["Jobs"])
async def write_job(job: Job):
    return JobListings.objects.if_not_exists().create(
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


@jobs.put("/jobs/update/{job_id}",
          response_model=Job,
          tags=["Jobs"])
async def update_job(job_id: str, job: Job):
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
    return JobListings.get(JobListings.uuid == job_id)


@jobs.delete("/jobs/delete/{job_id}", tags=["Jobs"])
async def delete_job(job_id: str):
    job = JobListings.get(JobListings.uuid == job_id)
    return JobListings.objects(
        uuid=job.uuid
    ).if_exists().delete()
