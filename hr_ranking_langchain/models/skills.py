
from typing import Any, Dict, Tuple
from langchain_core.pydantic_v1 import BaseModel, Field

class SkillNumberOfYearsResponse(BaseModel):
    has_skill: bool = Field(
        ...,
        description="describes whether the candidate has experience in the current skill",
    )
    number_of_years_with_skill: int = Field(
        ...,
        description="describes how many years of experience the candidate has in the current skill",
    )
    skill: str


class SkillNumberOfYearsResponseWithWeight(BaseModel):
    skill_number_of_years_response: SkillNumberOfYearsResponse
    score_weight: int
    

def create_skill_schema(skill: str) -> Tuple[Dict[str, Any], str, str]:
    skill = skill.replace(" ", "_")
    has_skill_field = f"document_mentions_{skill}_experience"
    number_of_years_with_skill = f"number_of_years_with_{skill}"
    schema = {
        "properties": {
            has_skill_field: {
                "type": "boolean",
                "description": f"describes whether the candidate has experience with {skill}",
            },
            number_of_years_with_skill: {
                "type": "integer",
                "description": f"describes how many years of experience the candidate has with {skill}. This should be zeo in case the skill {skill} is not mentioned.",
            },
        },
        "required": [has_skill_field, number_of_years_with_skill],
    }
    return schema, has_skill_field, number_of_years_with_skill

def parse_number_of_year_response_json(
    res: Dict
) -> SkillNumberOfYearsResponse:
    has_experience = res.get("has_experience")
    numberOfYears = res.get("number_of_years")
    skill = res.get("skill")
    response = SkillNumberOfYearsResponse(
        has_skill=has_experience, number_of_years_with_skill=numberOfYears, skill=skill
    )
    return response
