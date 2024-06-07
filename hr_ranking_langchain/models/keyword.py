from typing import List
from langchain_core.pydantic_v1 import BaseModel, Field

class TechnicalKeywords(BaseModel):
    keywords: List[str] = Field(
        ...,
        description="list of keywords which seem to be a technology or a skill",
    )

