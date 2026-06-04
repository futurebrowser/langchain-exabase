import os
import asyncio

from exabase import Exabase
from pydantic_ai import Agent
from exabase_pydantic_ai import exabase_memory_instructions


# Set up the Exabase client
client = Exabase(api_key=os.environ.get("EXABASE_API_KEY", "your-api-key"))

# Create an agent that automatically pulls relevant context into every run
agent = Agent(
    "openai-responses:gpt-5.5",
    instructions=[
        "You are a helpful assistant.",
        exabase_memory_instructions(client, query="user preferences and history")
    ],
)


async def main():
    # This run will automatically include any relevant memories found in Exabase
    # based on the 'query' provided in exabase_memory_instructions.
    print("Running agent with auto-injected context...")
    result = await agent.run("What can you tell me about me?")
    print(f"Agent response: {result.output}")


if __name__ == "__main__":
    asyncio.run(main())
