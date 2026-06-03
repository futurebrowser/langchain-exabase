import os

from langchain.agents import create_agent

from exabase import Exabase
from exabase_langchain import ExabaseToolkit

EXABASE_API_KEY = os.environ["EXABASE_API_KEY"]
EXABASE_BASE_ID = os.getenv("EXABASE_BASE_ID")
MODEL = os.getenv("OPENAI_MODEL", "openai:gpt-4.1-mini")

client = Exabase(api_key=EXABASE_API_KEY, base_id=EXABASE_BASE_ID)
tools = ExabaseToolkit(client=client).get_tools()
agent = create_agent(model=MODEL, tools=tools)

result = agent.invoke({"messages": [{"role": "user", "content": "Store that I like pistachio ice cream."}]})
print(result)
