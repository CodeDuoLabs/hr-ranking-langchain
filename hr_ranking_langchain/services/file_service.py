
from langchain.schema import Document
import chainlit.types as types

from hr_ranking_langchain.config import cfg
from hr_ranking_langchain.logger import logger


def write_temp_file(file: types.AskFileResponse) -> str:
    temp_doc_location = cfg.temp_doc_location
    new_path = temp_doc_location / (file.name)
    logger.info(f"new path: {new_path}")
    
    with open(file.path, "r") as f:
        content = f.read()
    
    with open(new_path, "wb") as f:
        f.write(content)
        
    return new_path
