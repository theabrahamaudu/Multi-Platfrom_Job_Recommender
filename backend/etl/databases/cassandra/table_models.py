from backend.etl.databases.cassandra.cassandra_conn import CassandraConn
from cassandra.cqlengine.models import Model
from cassandra.cqlengine.columns import (
    UUID, Text, DateTime, Boolean, List, Set, Map
)
from uuid import uuid4
from datetime import datetime

conn = CassandraConn()


class Users(Model):
    __connection__ = conn.session_name
    __keyspace__ = conn.keyspace_name
    __table_name__ = conn.users_table
    user_id = UUID(primary_key=True, default=uuid4)
    created_at = DateTime(default=datetime.now)
    username = Text(required=True, primary_key=True)
    first_name = Text(required=True)
    last_name = Text()
    email = Text()
    password = Text(required=True)
    skills = Set(Text)
    work_history = List(Map(Text, Text))
    preferences = Map(Text, Text)


class JobListings(Model):
    __connection__ = conn.session_name
    __keyspace__ = conn.keyspace_name
    __table_name__ = conn.jobs_table
    uuid = UUID(required=True, primary_key=True)
    skipped = Boolean()
    scraped_at = DateTime(required=True)
    source = Text()
    job_id = Text()
    job_title = Text(required=True)
    company_name = Text()
    location = Text()
    date = Text()
    job_link = Text(required=True)
    job_desc = Text(required=True)
    seniority = Text()
    emp_type = Text()
    job_func = Text()
    ind = Text()


class SearchMetadata(Model):
    __connection__ = conn.session_name
    __keyspace__ = conn.keyspace_name
    __table_name__ = conn.search_table
    user_id = Text(index=True)
    search_id = UUID(primary_key=True, default=uuid4)
    search_timestamp = DateTime(default=datetime.now,
                                primary_key=True,
                                clustering_order="desc")
    search_query = Text()
    search_results = List(UUID)


class ClicksMetadata(Model):
    __connection__ = conn.session_name
    __keyspace__ = conn.keyspace_name
    __table_name__ = conn.clicks_table
    user_id = Text(index=True)
    click_id = UUID(primary_key=True, default=uuid4)
    click_timestamp = DateTime(default=datetime.now,
                               primary_key=True,
                               clustering_order="desc")
    job_id = Text(required=True)
