from etl.databases.chroma.chroma_conn import ChromaConn
from etl.databases.chroma.data_models import JobEmbedding
from etl.load.load_cassandra import CassandraIO, JobListings
from etl.transform.vectorizer import vectorize
from src.utils.pipeline_log_config import pipeline as logger
from datetime import datetime


class ChromaIO(CassandraIO):
    def __init__(self):
        """
        Initializes a ChromaIO instance.

        This method initializes a ChromaIO instance, inheriting from
        CassandraIO. It sets up the connection to the Chroma database and
        initializes the jobs_table attribute by obtaining the collection
        from the Chroma database with the specified collection name
        and embedding function.

        Args:
        - None

        Returns:
        - None

        Example:
            chroma_io = ChromaIO()
            Initializes a ChromaIO instance, setting up the Chroma database
            connection and initializing the jobs_table attribute.
        """
        self.chroma_conn = ChromaConn()
        CassandraIO.__init__(self)

        self.jobs_table = self.chroma_conn.session.get_collection(
            name=self.chroma_conn.collection_name,
            embedding_function=self.chroma_conn.embedding_function
        )

    def get_vector_uuids(self):
        """
        Fetches UUIDs of jobs already present in the vector table.

        This method retrieves UUIDs corresponding to the jobs already existing
        in the vector table from the Chroma database. It stores the fetched
        UUIDs in the `vector_uuids` attribute of the ChromaIO instance.

        Args:
        - None

        Returns:
        - None

        Example:
            chroma_io = ChromaIO()

            chroma_io.get_vector_uuids()

            Fetches UUIDs of jobs existing in the vector table and
            stores them in the `vector_uuids` attribute.
        """
        try:
            # get uuids for jobs already in the vector table
            self.vector_uuids = self.jobs_table.get()["ids"]
            logger.info(f"Found {len(self.vector_uuids)} jobs in vector table")
        except Exception as e:
            logger.error(
                f"Failed to get vector uuids from Chroma: {e}"
            )
            logger.warning("Setting vector uuids to empty list")
            self.vector_uuids = []

    def load_from_cassandra(self):
        """
        Loads jobs from Cassandra to Chroma's vector table.

        This method fetches job UUIDs from both Cassandra and the vector table
        in the Chroma database. It identifies the jobs that have not been
        embedded yet by comparing UUIDs and proceeds to embed them using their
        respective data fetched from Cassandra. It pushes the newly embedded
        jobs to the vector table in Chroma.

        Args:
        - None

        Returns:
        - None

        Example:
            chroma_io = ChromaIO()

            chroma_io.load_from_cassandra()

            Fetches job UUIDs, identifies non-embedded jobs, embeds them,
            and pushes to the vector table.
        """
        # fetch job uuids from cassandra and chroma
        self.get_vector_uuids()
        self.get_uuids()

        # get list of jobs which have not been embedded yet
        to_push = [x for x in self.uuids if x not in self.vector_uuids]
        if len(to_push) > 0:
            # embed jobs in `to_push`
            uuid_list = []
            vector_list = []
            for id in to_push:
                # pull full job data from cassandra
                job = dict(JobListings.objects(uuid=id).get())
                # vectorize job data
                job_vector = JobEmbedding(
                    uuid=str(id),
                    embedding=vectorize(job)
                )
                # append uuid and vector to respective lists
                uuid_list.append(job_vector.uuid)
                vector_list.append(job_vector.embedding[0])

            logger.info(f"Pushing {len(uuid_list)} jobs to vector table")
            try:
                self.jobs_table.add(
                    ids=uuid_list,
                    embeddings=vector_list
                )
            except Exception as e:
                logger.error(
                    f"Failed to push jobs to vector table: {e}"
                )
        else:
            logger.info("Vector table is up to date")

    def scrub_jobs(self):
        """
        Deletes embeddings for jobs older than 30 days from
        the vector table in Chroma.

        This method fetches job UUIDs and their scrape dates from Cassandra.
        It identifies jobs older than 30 days based on their scrape dates and
        proceeds to delete their embeddings from the vector table in Chroma.

        Args:
        - None

        Returns:
        - None

        Example:
            chroma_io = ChromaIO()

            chroma_io.scrub_jobs()

            Fetches job UUIDs and their scrape dates, identifies old jobs,
            and deletes their embeddings.
        """
        # get job uuids and their scrape dates
        self.get_uuids()
        self.get_scrape_dates()

        # get jobs older than 30 days
        old_jobs = []
        for uuid, scrape_date in zip(self.uuids, self.scrape_dates):
            if datetime.today() - scrape_date >= 30:
                old_jobs.append(uuid)
        # delete embeddings for jobs older than 30 days
        self.jobs_table.delete(
            ids=old_jobs
        )
