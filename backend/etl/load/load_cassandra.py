from backend.etl.databases.cassandra.data_models import Job
from backend.etl.databases.cassandra.table_models import JobListings
from backend.etl.databases.cassandra.cassandra_conn import CassandraConn


class CassandraIO:
    def __init__(self):
        self.conn = CassandraConn()
        self.session = self.conn.session

    def get_uuids(self):
        uuids_set = self.session.execute(
            "SELECT uuid FROM job_listings"
        )
        self.uuids = []
        for i in uuids_set:
            self.uuids.append(str(i['uuid']))

    def write_jobs(self, jobs: list[Job]):
        # write new jobs
        n=0
        for job in jobs:
            n += 1
            try:
                JobListings.objects.if_not_exists().create(
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
            except Exception as e:
                e = str(e)
                print(f"job {n} already exists")
