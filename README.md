## Installation

```
poetry install
```

## Running

### Running the main application

```
chainlit run ./hr_ranking_langchain/ui/hr_ranking_langchain_chainlit.py --port 8080
```



## Configuration

This is the content of the `.env` file, which needs to be saved in the project root folder.

```
OPENAI_API_KEY=<open-api-key>
OPENAI_MODEL=<model>
REQUEST_TIMEOUT=300

VERBOSE_LLM=true
LANGCHAIN_CACHE=false
CHATGPT_STREAMING=false

# UI
SHOW_CHAIN_OF_THOUGHT=true

# Token limit for chatgpt.
TOKEN_LIMIT=6000
```
