from backend.etl.databases.cassandra.data_models import Job
from backend.etl.databases.cassandra.table_models import JobListings
from backend.etl.databases.cassandra.cassandra_conn import CassandraConn
from datetime import datetime


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

    def get_scrape_dates(self):
        scrape_dates_set = self.session.execute(
            "SELECT scraped_at FROM job_listings"
        )
        self.scrape_dates = []
        for i in scrape_dates_set:
            self.scrape_dates.append(i['scraped_at'])

    def write_jobs(self, jobs: list[Job]):
        # write new jobs
        for job in jobs:
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
                pass

    def scrub_jobs(self):
        self.get_uuids()
        self.get_scrape_dates()
        old_jobs = []
        for uuid, scrape_date in zip(self.uuids, self.scrape_dates):
            if datetime.today() - scrape_date >= 30:
                old_jobs.append(uuid)

        for uuid in old_jobs:
            try:
                JobListings.objects(uuid=uuid).if_exists().delete()
            except Exception as e:
                e = str(e)
                pass
