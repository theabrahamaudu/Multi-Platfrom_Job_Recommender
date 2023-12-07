"""
This module contains necessary read-write methods for loading data to and from
Cassandra in the ETL pipeline.
"""
from etl.databases.cassandra.data_models import Job
from etl.databases.cassandra.table_models import JobListings
from etl.databases.cassandra.cassandra_conn import CassandraConn
from src.utils.pipeline_log_config import pipeline as logger
from datetime import datetime


class CassandraIO:
    def __init__(self):
        self.conn = CassandraConn()
        self.session = self.conn.session

    def get_uuids(self):
        """
        Retrieves job UUIDs from the `job_listings` table in the
        connected Cassandra database.

        This method performs a query to fetch all the UUIDs present in the
        job_listings table of the connected Cassandra database. It executes
        the query through the session attribute, storing the fetched UUIDs.

        The UUIDs retrieved from the job_listings table are parsed from
        the response dictionary and appended to a list (self.uuids), providing
        access to these UUIDs for comparison and verification
        during job scraping and vetor database updates.

        Args:
        - None

        Returns:
        - None

        Example:
            cassandra_io = CassandraIO()

            cassandra_io.get_uuids()

            Retrieves job UUIDs from the job_listings table in the connected
            Cassandra database and stores them in the CassandraIO instance
            for reference during job scraping and vector database updates.
        """
        # get job uuids from database
        uuids_set = self.session.execute(
            "SELECT uuid FROM job_listings"
        )

        # parse the dictionary response and append
        # each uuid to a growing list
        self.uuids = []
        for i in uuids_set:
            self.uuids.append(str(i['uuid']))

    def get_scrape_dates(self):
        """
        Retrieves job scrape dates from the job_listings table
        in the connected Cassandra database.

        This method executes a query to fetch all the 'scraped_at' dates
        present in the job_listings table of the connected Cassandra database.
        It utilizes the session attribute to execute the query, storing the
        fetched scrape dates in a list (self.scrape_dates).

        These scraped dates, collected from the job_listings table,
        are stored in the CassandraIO instance. They can be
        referenced for comparison or utilization, such as for the
        identification and potential deletion of older jobs.

        Args:
        - None

        Returns:
        - None

        Example:
            cassandra_io = CassandraIO()

            cassandra_io.get_scrape_dates()

            Retrieves job scrape dates from the job_listings table in the
            connected Cassandra database and stores them in the CassandraIO
            instance for potential usage, like identifying and
            handling older job entries.
        """
        # fetch job scrape dates from database
        scrape_dates_set = self.session.execute(
            "SELECT scraped_at FROM job_listings"
        )

        # parse into list to be referenced for
        # deleting old jobs
        self.scrape_dates = []
        for i in scrape_dates_set:
            self.scrape_dates.append(i['scraped_at'])

    def write_jobs(self, jobs: list[Job]):
        # write new jobs
        logger.info(f"Writing {len(jobs)} new jobs")
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
                logger.error(f"Error writing jobs: {e}")

    def scrub_jobs(self):
        """
        Scrubs and potentially deletes jobs older than 30 days
        from the `job_listings` table.

        This method initiates the process of scrubbing jobs that are
        considered more than 30 days old based on their 'scraped_at' dates,
        as stored in the CassandraIO instance. It fetches job UUIDs and their
        respective scrape dates by invoking the `get_uuids` and
        `get_scrape_dates` methods.

        After retrieving this information, it compares the scrape dates with
        the current date. Any jobs with scrape dates more than 30 days old are
        collected and appended to the 'old_jobs' list.
        It logs the number of such jobs found.

        Subsequently, it attempts to delete these old jobs from the
        job_listings table using the UUIDs collected in 'old_jobs'.
        It logs the successful deletion of these old job entries from
        the 'job_listings' table.

        Args:
        - None

        Returns:
        - None

        Example:
            cassandra_io = CassandraIO()

            cassandra_io.scrub_jobs()

            Initiates the scrubbing process to identify and potentially delete
            jobs older than 30 days from the job_listings table in
            the connected Cassandra database.
        """
        # fetch jobs and their scrape dates
        self.get_uuids()
        self.get_scrape_dates()

        # compare scrape dates with current date and append
        # jobs that are more than 30 days old to list
        old_jobs = []
        for uuid, scrape_date in zip(self.uuids, self.scrape_dates):
            if datetime.today() - scrape_date >= 30:
                old_jobs.append(uuid)
        logger.info(f"Found {len(old_jobs)} jobs more than 30 days old")

        # delete old jobs
        for uuid in old_jobs:
            try:
                JobListings.objects(uuid=uuid).if_exists().delete()
                logger.info(
                    f"Deleted {len(old_jobs)} old jobs from `job_listings`"
                )
            except Exception as e:
                logger.error(f"Error deleting jobs: {e}")
