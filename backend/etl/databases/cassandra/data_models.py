from typing import List, Set, OrderedDict
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class User(BaseModel):
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
    db_uuid: UUID
    uuid: str = Field(strict=True, min_length=32, max_length=36)
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
    user_id: UUID
    search_id: UUID
    search_timestamp: datetime
    search_query: str = Field(min_length=1)
    search_results: List[UUID] = Field(default_factory=list[UUID])


class Click(BaseModel):
    user_id: UUID
    click_id: UUID
    click_timestamp: datetime
    job_id: UUID
