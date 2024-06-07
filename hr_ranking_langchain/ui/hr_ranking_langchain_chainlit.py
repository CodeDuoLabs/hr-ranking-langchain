from pathlib import Path
from typing import List, Optional, Tuple
import chainlit as cl
import chainlit.types as types
from langchain.schema import Document

from hr_ranking_langchain.models.candidate import CandidateInfo, sort_candidate_infos
from hr_ranking_langchain.plot.bar_chart import create_barchart
from hr_ranking_langchain.services.document_service import convert_to_document
from hr_ranking_langchain.services.evaluation_service import process_docs
from hr_ranking_langchain.services.keyword_service import extract_keywords_from_text
from hr_ranking_langchain.toml_support import prompts
from hr_ranking_langchain.ui.avatar_factory import AVATAR, setup_avatar

MAX_FILES = 20
TIMEOUT = 600

async def initial_message() -> str:
    question = prompts["question_initial"]

    response =  await cl.AskUserMessage(
        content=question["message"],
        author=AVATAR["CHATBOT"],
        timeout=TIMEOUT,
    ).send()
    return response['output']

@cl.step
async def skills_weight_message(skills: List[str]) -> str:
    question = prompts["question_skills_weight"]
    skills_list = "\n- ".join([f"{f}" for f in skills])

    weights = await cl.AskUserMessage(
        content=question["message"].format(skills=skills_list, length= len(skills)),
        author=AVATAR["CHATBOT"],
        timeout=TIMEOUT,
    ).send()
    
    weights = [int(i.strip()) for i in weights['output'].split(",")]
    
    return weights


async def upload_file_messages() -> str:
    question = prompts["question_upload_file"]

    return await cl.AskUserMessage(
        content=question["message"],
        author=AVATAR["CHATBOT"],
        timeout=TIMEOUT,
    ).send()


@cl.step
async def processing_file_message(docs: List[Document], skills: List[str], weights: List[int], file_names:str) :
    update = prompts["update_file_message"]

    msg = cl.Message(
        content="",
        author=AVATAR["CHATBOT"],
    )
    
    await msg.stream_token(update["message"].format(file_names=file_names, length= len(docs)))
    
    async def on_stream(text: str):
        await msg.stream_token(text)
    
    candidate_infos = await process_docs(docs, skills, weights, stream=on_stream)
    candidate_infos: List[CandidateInfo] = sort_candidate_infos(candidate_infos)
    
    barchart_image = create_barchart(candidate_infos)
    elements = [
        cl.Image(
            name="image1",
            display="inline",
            path=str(barchart_image.absolute()),
            size="large",
        )
    ]

    barchart_message = cl.Message(content="## Results", elements=elements)
    await barchart_message.send()
    
    await execute_candidates(candidate_infos)

async def error_skills_weight_message() :
    question = prompts["error_skills_weight"]

    return await cl.Message(
        content=question["message"],
        author=AVATAR["CHATBOT"],
    ).send()

@cl.on_chat_start
async def init():
    await setup_avatar()
    job_description = await initial_message()

    skills = extract_keywords_from_text(job_description).keywords
        
    weights = await process_skill_weights(skills)
                
    docs, files = await process_files()
    file_names = "\n- ".join([f"{f.name}" for f in files])
    await processing_file_message(docs=docs, skills=skills, weights=weights, file_names=file_names)
    

async def process_files() -> Tuple[List[Document], types.AskFileResponse] :
    docs: List[Document] = []
    files= []
    while not files:
        files = await cl.AskFileMessage(
            content="Please upload multiple pdf files with the CV of a candidate!",
            accept=["application/pdf"],
            author=AVATAR["CHATBOT"],
            max_files=MAX_FILES,
            timeout=TIMEOUT,
        ).send()
        
        if files is not None:
            docs.extend([convert_to_document(file) for file in files]) 
    
    return docs, files

@cl.step
async def process_skill_weights(skills)-> List[str]:
    while True:
        weights = await skills_weight_message(skills)
        
        if len(skills) == len(weights):
            return weights
        else:
            await error_skills_weight_message()

@cl.step
def ranking_generator(candidate_infos: List[CandidateInfo]):
    for i, candidate_info in enumerate(candidate_infos):
        personal_data = candidate_info.candidate_info_response
        source_file = Path(candidate_info.source_file)
        
        yield i, candidate_info, personal_data, source_file


@cl.step
async def execute_candidates(candidate_infos: List[CandidateInfo]):
    ranking_text = "## Ranking\n\n"
    for i, candidate_info, personal_data, source_file in ranking_generator(candidate_infos):
        personal_data = candidate_info.candidate_info_response
        source_file = Path(candidate_info.source_file)
        ranking_text += f"{i + 1}. Name: **{personal_data.name}**"
        ranking_text += f"* {source_file.name}*\n\n"

    await cl.Message(
        content=ranking_text,
        author=AVATAR["CHATBOT"],
    ).send()

    for i, candidate_info, personal_data, source_file in ranking_generator(candidate_infos):
        pdf_element = create_pdf(source_file)
        personal_data = candidate_info.candidate_info_response
        source_file = Path(candidate_info.source_file)
        ranking_text = "## Breakdown\n\n"
        ranking_text += f"{i + 1}. Name: **{personal_data.name}**, Email: {personal_data.email}, Experience: {personal_data.years_of_experience}, points: {candidate_info.score}\n\n"
        ranking_text += f"*{source_file}*\n\n"
        
        for nyr in candidate_info.number_of_years_responses:
            number_of_years_response = nyr.skill_number_of_years_response
            ranking_text += f"  - Skill: {number_of_years_response.skill}, years: {number_of_years_response.number_of_years_with_skill}\n"
        
        await cl.Message(
            content=ranking_text,
            elements=[pdf_element],
            author=AVATAR["CHATBOT"],
        ).send()

def create_pdf(source_file: Path) -> Optional[cl.File]:
    return cl.File(
        name=source_file.name, display="inline", path=str(source_file.absolute())
    )