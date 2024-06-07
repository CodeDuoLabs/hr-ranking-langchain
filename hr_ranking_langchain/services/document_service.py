
from langchain.schema import Document
from langchain_community.document_loaders import PyPDFium2Loader
import chainlit.types as types

from typing import List, Optional
from pathlib import Path

from hr_ranking_langchain.config import cfg
from hr_ranking_langchain.logger import logger

def extract_data(path: Path, filter: Optional[str] = None) -> List[Document]:
    assert path.exists(), f"Path {path} does not exist."
    res: List[Document] = []
    pdfs = list(path.glob("*.pdf"))
    logger.info(f"There are {len(pdfs)} physical documents.")
    for pdf in pdfs:
        if filter is None or filter in pdf.stem:
            new_document = convert_to_document(pdf)
            res.append(new_document)
    return res

def convert_to_document(file: types.AskFileResponse) -> Document:
    loader = PyPDFium2Loader(str(file.path))
    pages: List[Document] = loader.load()
    metadata = pages[0].metadata
    pdf_content = ""
    for p in pages:
        pdf_content += p.page_content
    new_document = Document(page_content=pdf_content, metadata=metadata)
    return new_document
