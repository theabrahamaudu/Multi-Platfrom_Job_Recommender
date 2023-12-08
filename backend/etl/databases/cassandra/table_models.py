"""
This module defines the table models for the Cassandra database.
"""
from etl.databases.cassandra.cassandra_conn import CassandraConn
from cassandra.cqlengine.models import Model
from cassandra.cqlengine.columns import (
    UUID, Text, DateTime, Boolean, List, Set, Map
)
from uuid import uuid4
from datetime import datetime

conn = CassandraConn()


class Users(Model):
    """
    Represents the `users` table in Cassandra.

    Attributes:
    - user_id (UUID): Primary key representing the user's unique identifier.
    - created_at (DateTime): Timestamp indicating the user's creation time.
    - username (Text): Unique username for the user.
    - first_name (Text): User's first name.
    - last_name (Text, optional): User's last name.
    - email (Text, optional): User's email address.
    - password (Text): User's password.
    - skills (Set[Text]): Set of skills associated with the user.
    - work_history (List[Map[Text, Text]]): List of dictionaries representing
      the user's work history.
    - preferences (Map[Text, Text]): Key-value pairs for user preferences.
    """
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
    """
    Represents the `job_listings` table in Cassandra.

    Attributes:
    - uuid (UUID): Primary key representing the unique identifier for each
      job listing.
    - skipped (Boolean, optional): Indicates whether the job was skipped
      during processing.
    - scraped_at (DateTime): Timestamp indicating when the job listing
      was scraped.
    - source (Text, optional): Source of the job listing.
    - job_id (Text, optional): ID associated with the job.
    - job_title (Text): Title of the job.
    - company_name (Text, optional): Name of the company offering the job.
    - location (Text, optional): Location of the job.
    - date (Text, optional): Date of the job posting.
    - job_link (Text): Link to the job listing.
    - job_desc (Text): Description of the job.
    - seniority (Text, optional): Level of seniority associated with the job.
    - emp_type (Text, optional): Type of employment for the job.
    - job_func (Text, optional): Function or role of the job.
    - ind (Text, optional): Industry associated with the job.
    """
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
    """
    Represents the `search_metadata` table in Cassandra.

    Attributes:
    - user_id (Text, indexed): Identifier for the user associated with
      the search.
    - search_id (UUID, primary key): Unique identifier for each search entry.
    - search_timestamp (DateTime, primary key): Timestamp of the search,
      sorted in descending order.
    - search_query (Text): The search query text.
    - search_results (List[UUID]): List of UUIDs representing search results.
    """
    __connection__ = conn.session_name
    __keyspace__ = conn.keyspace_name
    __table_name__ = conn.search_table
    user_id = Text(index=True)
    search_id = UUID(primary_key=True, default=uuid4)
    search_timestamp = DateTime(
        default=datetime.now,
        primary_key=True,
        clustering_order="desc"
    )
    search_query = Text()
    search_results = List(UUID)


class ClicksMetadata(Model):
    """
    Represents the `clicks_metadata` table in Cassandra.

    Attributes:
    - user_id (Text, indexed): Identifier for the user associated with
      the click.
    - click_id (UUID, primary key): Unique identifier for each click entry.
    - click_timestamp (DateTime, primary key): Timestamp of the click,
      sorted in descending order.
    - job_id (Text, required): Identifier of the job associated with the click.
    """
    __connection__ = conn.session_name
    __keyspace__ = conn.keyspace_name
    __table_name__ = conn.clicks_table
    user_id = Text(index=True)
    click_id = UUID(primary_key=True, default=uuid4)
    click_timestamp = DateTime(
        default=datetime.now,
        primary_key=True,
        clustering_order="desc"
    )
    job_id = Text(required=True)
