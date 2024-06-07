from typing import Any, List
from langchain.chains import create_tagging_chain_pydantic

from hr_ranking_langchain.models.keyword import TechnicalKeywords
from hr_ranking_langchain.config import cfg


def extract_keywords(expression_list: List[str]) -> List[Any]:
    expression_pairs = []
    for expression in expression_list:
        technical_keywords: TechnicalKeywords = extract_keywords_from_text(expression)
        technical_keywords.keywords = [k.lower() for k in technical_keywords.keywords]
        expression_pairs.append((expression, technical_keywords.keywords))
    return expression_pairs


def extract_keywords_from_text(job_description :str) -> TechnicalKeywords:
    chain = create_tagging_chain_pydantic(TechnicalKeywords, cfg.llm, verbose=cfg.verbose_llm)
    return chain.run(job_description)
