from typing import List
from uuid import UUID
from pydantic import BaseModel


class JobEmbedding(BaseModel):
    uuid: UUID
    embedding: List[float]
