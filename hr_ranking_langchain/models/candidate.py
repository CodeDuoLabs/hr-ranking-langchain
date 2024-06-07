from pathlib import Path
from typing import Dict, List, Optional

from langchain_core.pydantic_v1 import BaseModel, Field
from .skills import SkillNumberOfYearsResponseWithWeight

class CandidateInfoResponse(BaseModel):
    name: Optional[str] = Field(
        ...,
        description="the name of the candidate if available in the text",
    )
    email: str = Field(
        ...,
        description="the email address of the candidate if available in the text",
    )
    phone: str = Field(
        ...,
        description="the phone number of the candidate if available in the text",
    )
    portfolio: str = Field(
        ...,
        description="the portfoilo website of the candiate if available in the text",
    )
    github: str = Field(
        ...,
        description="the github url of the candiate if available in the text. Should have the pattern https://github.com/<username>",
    )
    github: str = Field(
        ...,
        description="the linkedin url of the candiate if available in the text. Should have the pattern https://linkedin.com/in/<username>",
    )
    present_job: str = Field(
        ...,
        description="the current position and company the candiate is working for  if available in the text.",
    )
    education: str = Field(
        ...,
        description="the latest or highest level of education of the candidate if available in the text.",
    )
    years_of_experience: Optional[int] = Field(
        ...,
        description="total years of professional experience",
    )


class CandidateInfo:
    candidate_info_response: CandidateInfoResponse
    number_of_years_responses: List[SkillNumberOfYearsResponseWithWeight]
    source_file: str
    score: int

    def __init__(
        self,
        candidate_info_response: CandidateInfoResponse,
        number_of_years_responses: List[SkillNumberOfYearsResponseWithWeight],
        source_file: Path,
    ):
        self.candidate_info_response = candidate_info_response
        self.number_of_years_responses = number_of_years_responses
        self.source_file = source_file
        self.calculate_score()

    def calculate_score(self):
        score = 0
        years_of_experience = self.candidate_info_response.years_of_experience
        if years_of_experience is None:
            years_of_experience = 0
        for number_of_years_response in self.number_of_years_responses:
            nyr = number_of_years_response.skill_number_of_years_response
            if nyr.has_skill:
                score += (
                    nyr.number_of_years_with_skill
                    * number_of_years_response.score_weight
                )
        self.score = score + years_of_experience

    def __repr__(self) -> str:
        return f"Name: {self.candidate_info_response.name}, score: {self.score}, source_file: {self.source_file}"


def sort_candidate_infos(candidate_infos: List[CandidateInfo]) -> List[CandidateInfo]:
    return sorted(candidate_infos, key=lambda x: x.score, reverse=True)



def parse_candidate_info_json(res: Dict) -> CandidateInfoResponse:
    name = res.get("name")
    if (
        name is not None
    ):
        return CandidateInfoResponse(name=name)
    return None
