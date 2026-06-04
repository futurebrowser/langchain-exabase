# Exabase Pydantic AI Integration

This package provides [Exabase](https://exabase.io) memory tools for [Pydantic AI](https://ai.pydantic.dev) agents.

## Installation

```bash
pip install exabase-pydantic-ai
```

## Usage

```python
from exabase import Exabase
from exabase_pydantic_ai import create_exabase_tools, exabase_memory_instructions
from pydantic_ai import Agent

client = Exabase(api_key="your-api-key")

agent = Agent(
    "openai:gpt-4o",
    tools=create_exabase_tools(client=client),
    instructions=[exabase_memory_instructions(client=client)],
)

result = await agent.run("What do you remember about my preferences?")
print(result.data)
```
