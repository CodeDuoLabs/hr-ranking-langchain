import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

from hr_ranking_langchain.logger import logger

class Config:
    model = os.getenv("OPENAI_MODEL")
    request_timeout = int(os.getenv("REQUEST_TIMEOUT"))
    has_langchain_cache = os.getenv("LANGCHAIN_CACHE") == "true"
    streaming = os.getenv("CHATGPT_STREAMING") == "true"

    llm = ChatOpenAI(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        model=model,
        temperature=0,
        request_timeout=request_timeout,
        cache=has_langchain_cache,
        streaming=streaming,
    )

    project_root = os.getcwd()
    verbose_llm = os.getenv("VERBOSE_LLM") == "true"

    show_chain_of_thought = os.getenv("SHOW_CHAIN_OF_THOUGHT") == "true"

    token_limit = int(os.getenv("TOKEN_LIMIT"))

    product_title = "arcab Lead Generation"


cfg = Config()

if __name__ == "__main__":
    logger.info("Model: %s", cfg.model)
    logger.info("Verbose: %s", cfg.verbose_llm)
    logger.info("Project Root: %s", cfg.project_root)
