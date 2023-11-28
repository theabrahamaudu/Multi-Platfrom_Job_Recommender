from backend.etl.databases.milvus.milvus_conn import MilvusConn
from backend.etl.databases.milvus.data_models import JobEmbedding
from backend.etl.databases.milvus.table_models import collection_name
from backend.etl.load.load_cassandra import CassandraIO, JobListings
from backend.etl.transform.vectorizer import vectorize
from pymilvus import Collection
from datetime import datetime


class MilvusIO(CassandraIO):
    def __init__(self):
        self.milvus_conn = MilvusConn()
        CassandraIO.__init__(self)

        self.jobs_table = Collection(
            name=collection_name,
            using=self.milvus_conn.session_name,
        )
        self.jobs_table.load()

    def get_vector_uuids(self):
        try:
            vector_uuid_set = self.jobs_table.query(
                expr="",
                output_fields=["uuid"],
                limit=16000
            )
            self.vector_uuids = []
            for i in vector_uuid_set:
                self.vector_uuids.append(str(i['uuid']))
        except Exception as e:
            print(e)

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
                embedding=vectorize(job).tolist()
            )
            uuid_list.append(job_vector.uuid)
            vector_list.append(job_vector.embedding)

        if len(uuid_list) > 0:
            self.jobs_table.insert([
                uuid_list,
                vector_list
            ])

    def scrub_jobs(self):
        self.get_uuids()
        self.get_scrape_dates()
        old_jobs = []
        for uuid, scrape_date in zip(self.uuids, self.scrape_dates):
            if datetime.today() - scrape_date >= 30:
                old_jobs.append(uuid)

        self.jobs_table.delete(
            expr=f"uuid in {old_jobs}",
        )

    def close(self):
        self.jobs_table.release()
        self.milvus_conn.close()
