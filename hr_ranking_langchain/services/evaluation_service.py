from typing import Callable, List, Any

from langchain.schema import Document
from langchain.prompts import (
    PromptTemplate,
)
from langchain.chains import create_tagging_chain_pydantic, create_tagging_chain

from hr_ranking_langchain.config import cfg
from hr_ranking_langchain.models.candidate import CandidateInfo, CandidateInfoResponse
from hr_ranking_langchain.models.skills import SkillNumberOfYearsResponse, SkillNumberOfYearsResponseWithWeight, create_skill_schema
from hr_ranking_langchain.logger import logger
from .skill_check_service import skill_check
from .keyword_service import extract_keywords


SKILL_TEMPLATE = PromptTemplate.from_template(
    "Based on the following text, how many years does this person have in {technology}.? "
    + "And tell whether this person has experience in {technology}."
    + "If a person has experience in {technology} but you cannot figure out the years reply with 1.\n\n"
)
async def process_docs(
    docs: List[Document],
    skills: List[str] ,
    weights: List[int],
    stream: Callable[[str], None]
) -> List[CandidateInfo]:
    
    candidate_infos: List[CandidateInfo] = []
    expression_pairs: List[Any] = extract_keywords(skills)
    extracted_strs = ",".join([str(ep[1]) for ep in expression_pairs])
    logger.info("Keywords: %s", extracted_strs)
    
    await stream(f"Extracted keywords: **{extracted_strs}**\n\n")
    
    for doc in docs:
        chain = create_tagging_chain_pydantic(CandidateInfoResponse, cfg.llm, verbose=cfg.verbose_llm)
        try:
            candidate_details = chain.run(doc)

            number_of_year_responses: List[SkillNumberOfYearsResponseWithWeight] = []
            await process_skills(
                doc, number_of_year_responses, expression_pairs, skills, weights, stream
            )
            candidate_info = CandidateInfo(
                candidate_info_response=candidate_details,
                number_of_years_responses=number_of_year_responses,
                source_file=doc.metadata["source"],
            )
            candidate_infos.append(candidate_info)
        except Exception as e:
            logger.error(f"Could not process {doc.metadata['source']} due to {e}")
            
    return candidate_infos


async def process_skills(
    doc: Document,
    number_of_year_responses: List[SkillNumberOfYearsResponseWithWeight],
    expression_pairs: List[Any],
    skills: List[str],
    weights: List[int],
    stream: Callable[[str], None]
):
    page_content = doc.page_content
    for skill, weight, expression_pair in zip(skills, weights, expression_pairs):
        _, extracted_keywords = expression_pair
        # Create skill schema dynamically
        schema, has_skill_field, number_of_years_with_skill = create_skill_schema(skill)
        chain = create_tagging_chain(schema, cfg.llm, verbose=cfg.verbose_llm)
        # Combine the CV with a question
        doc.page_content = SKILL_TEMPLATE.format(technology=skill) + page_content
        # Run the chain
        number_of_years_response_json = chain.run(doc)
        # Extract the results
        number_of_years = (
            0
            if number_of_years_response_json[number_of_years_with_skill] == None
            else number_of_years_response_json[number_of_years_with_skill]
        )
        has_skill = (
            False
            if not number_of_years_response_json[has_skill_field]
            else number_of_years_response_json[has_skill_field]
        )
        # Verify if keywords are present to prevent hallucinations
        matches = skill_check(page_content, extracted_keywords)
        if matches == False:
            number_of_years = 0
            has_skill = False
            logger.info("Cannot find keywords: %s", extracted_keywords)
        else:
            if number_of_years == 0:
                number_of_years = 1  # Assume the skill is there at least for one year
                has_skill = True
        skill_number_of_years_response = SkillNumberOfYearsResponse(
            has_skill=has_skill, number_of_years_with_skill=number_of_years, skill=skill
        )
        number_of_year_responses.append(
            SkillNumberOfYearsResponseWithWeight(
                skill_number_of_years_response=skill_number_of_years_response,
                score_weight=weight,
            )
        )
        logger.info(f"Response: {skill_number_of_years_response}")
