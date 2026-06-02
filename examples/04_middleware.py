import os

from langchain.agents import create_agent

from langchain_exabase import Exabase, exabase_memory_middleware

EXABASE_API_KEY = os.environ["EXABASE_API_KEY"]
EXABASE_BASE_ID = os.getenv("EXABASE_BASE_ID")
MODEL = os.getenv("OPENAI_MODEL", "openai:gpt-4.1-mini")

client = Exabase(api_key=EXABASE_API_KEY, base_id=EXABASE_BASE_ID)
middleware = exabase_memory_middleware(client=client, namespace=("memories",), limit=4)

agent = create_agent(model=MODEL, middleware=[middleware])

result = agent.invoke({"messages": [{"role": "user", "content": "What do you remember about me?"}]})
print(result)
