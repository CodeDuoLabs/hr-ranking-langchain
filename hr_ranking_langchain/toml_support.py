from pathlib import Path
import tomli

from hr_ranking_langchain.config import cfg

def read_toml(file: Path) -> dict:
    with open(file, "rb") as f:
        return tomli.load(f)


def read_prompts_toml() -> dict:
    return read_toml(f"{cfg.project_root}/prompts.toml")


prompts = read_prompts_toml()
