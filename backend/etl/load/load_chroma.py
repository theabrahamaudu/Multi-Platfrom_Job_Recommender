from etl.databases.chroma.chroma_conn import ChromaConn
from etl.databases.chroma.data_models import JobEmbedding
from etl.load.load_cassandra import CassandraIO, JobListings
from etl.transform.vectorizer import vectorize
from datetime import datetime


class ChromaIO(CassandraIO):
    def __init__(self):
        self.chroma_conn = ChromaConn()
        CassandraIO.__init__(self)

        self.jobs_table = self.chroma_conn.session.get_collection(
            name=self.chroma_conn.collection_name,
            embedding_function=self.chroma_conn.embedding_function
        )

    def get_vector_uuids(self):
        try:
            self.vector_uuids = self.jobs_table.get()["ids"]
        except Exception as e:
            print(e)
            self.vector_uuids = []

    def load_from_cassandra(self):
        self.get_vector_uuids()
        self.get_uuids()

        uuid_list = []
        vector_list = []
        to_push = [x for x in self.uuids if x not in self.vector_uuids]
        print("To push: ", len(to_push))
        for id in to_push:
            job = dict(JobListings.objects(uuid=id).get())
            job_vector = JobEmbedding(
                uuid=str(id),
                embedding=vectorize(job)
            )
            uuid_list.append(job_vector.uuid)
            vector_list.append(job_vector.embedding[0])

        if len(uuid_list) > 0:
            self.jobs_table.add(
                ids=uuid_list,
                embeddings=vector_list
            )

    def scrub_jobs(self):
        self.get_uuids()
        self.get_scrape_dates()
        old_jobs = []
        for uuid, scrape_date in zip(self.uuids, self.scrape_dates):
            if datetime.today() - scrape_date >= 30:
                old_jobs.append(uuid)

        self.jobs_table.delete(
            ids=old_jobs
        )
