import os

from langchain.agents import create_agent
from langmem import create_manage_memory_tool, create_search_memory_tool

from langchain_exabase import Exabase, ExabaseStore

EXABASE_API_KEY = os.environ["EXABASE_API_KEY"]
EXABASE_BASE_ID = os.getenv("EXABASE_BASE_ID")
MODEL = os.getenv("OPENAI_MODEL", "openai:gpt-4.1-mini")

client = Exabase(api_key=EXABASE_API_KEY, base_id=EXABASE_BASE_ID)
store = ExabaseStore(client)

manage_memory = create_manage_memory_tool(namespace=("memories", "{langgraph_user_id}"), store=store)
search_memory = create_search_memory_tool(namespace=("memories", "{langgraph_user_id}"), store=store)

agent = create_agent(model=MODEL, tools=[manage_memory, search_memory], store=store)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "Remember that I work on Exabase memory."}]},
    config={"configurable": {"langgraph_user_id": "demo-user"}},
)
print(result)
