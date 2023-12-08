"""
This module contains the data models for the Cassandra database.
"""
from typing import List, Set, OrderedDict
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class User(BaseModel):
    """
    Represents a user with various attributes and preferences.

    Attributes:
    - user_id (UUID4): Unique identifier for the user.
    - created_at (datetime): Timestamp indicating user creation time.
    - username (str): User's username (1 to 128 characters).
    - first_name (str): User's first name (1 to 128 characters).
    - last_name (str, optional): User's last name (default: "Not specified").
    - email (str, optional): User's email (default: "Not specified").
    - password (str): User's password (1 to 128 characters).
    - skills (Set[str]): User's set of skills (default: empty set).
    - work_history (List[OrderedDict[str, str]]): User's work history
      (default: empty list of dictionaries with string keys and values).
    - preferences (OrderedDict[str, str]): User's preferences
      (default: empty ordered dictionary with string keys and values).
    """
    user_id: UUID
    created_at: datetime
    username: str = Field(min_length=1, max_length=128)
    first_name: str = Field(min_length=1, max_length=128)
    last_name: str = Field(default="Not specified")
    email: str = Field(default="Not specified")
    password: str = Field(min_length=1, max_length=128)
    skills: Set[str] = Field(default_factory=set[str])
    work_history: List[OrderedDict[str, str]] =\
        Field(default_factory=list[dict[str, str]])
    preferences: OrderedDict[str, str] = Field(default_factory=dict[str, str])


class Job(BaseModel):
    """
    Represents a job listing with various attributes.

    Attributes:
    - uuid (UUID4): Unique identifier for the job.
    - skipped (bool): Indicates if the job was skipped during scraping.
    - scraped_at (datetime): Timestamp when the job was scraped.
    - source (str): Source of the job listing.
    - job_id (str): Identifier for the job.
    - job_title (str): Title of the job (minimum length: 1 character).
    - company_name (str): Name of the company offering the job.
    - location (str): Location of the job.
    - date (str): Date of the job posting.
    - job_link (str): Link to the job (minimum length: 1 character).
    - job_desc (str): Job description (minimum length: 1 character).
    - seniority (str): Level of seniority associated with the job.
    - emp_type (str): Type of employment associated with the job.
    - job_func (str): Function or role related to the job.
    - ind (str): Industry associated with the job.
    """
    uuid: UUID
    skipped: bool
    scraped_at: datetime
    source: str
    job_id: str
    job_title: str = Field(min_length=1)
    company_name: str
    location: str
    date: str
    job_link: str = Field(min_length=1)
    job_desc: str = Field(min_length=1)
    seniority: str
    emp_type: str
    job_func: str
    ind: str


class Search(BaseModel):
    """
    Represents a search performed by a user.

    Attributes:
    - user_id (UUID4): Unique identifier of the user performing the search.
    - search_id (UUID4): Unique identifier for this specific search.
    - search_timestamp (datetime): Timestamp of when the search was conducted.
    - search_query (str): Query string used for the search
      (minimum length: 1 character).
    - search_results (List[UUID4]): List of UUIDs representing search results.
    """
    user_id: UUID
    search_id: UUID
    search_timestamp: datetime
    search_query: str = Field(min_length=1)
    search_results: List[UUID] = Field(default_factory=list[UUID])


class Click(BaseModel):
    """
    Represents a user click on a job listing.

    Attributes:
    - user_id (UUID4): Unique identifier of the user who clicked.
    - click_id (UUID4): Unique identifier for this specific click event.
    - click_timestamp (datetime): Timestamp of when the click occurred.
    - job_id (UUID4): Unique identifier of the job that was clicked.
    """
    user_id: UUID
    click_id: UUID
    click_timestamp: datetime
    job_id: UUID
