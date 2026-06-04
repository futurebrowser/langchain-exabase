import os
import asyncio

from exabase import Exabase
from pydantic_ai import Agent
from exabase_pydantic_ai import create_exabase_tools


# Set up the Exabase client
client = Exabase(api_key=os.environ.get("EXABASE_API_KEY", "your-api-key"))

# Create an agent with Exabase tools
agent = Agent(
    "openai-responses:gpt-5.5",
    tools=create_exabase_tools(client),
    system_prompt="You are a helpful assistant with long-term memory.",
)


async def main():
    # Store a memory
    print("Storing memory...")
    await agent.run("My favorite color is deep space blue. Please remember that.")

    # Retrieve the memory
    print("Retrieving memory...")
    result = await agent.run("What is my favorite color?")
    print(f"Agent response: {result.output}")


if __name__ == "__main__":
    asyncio.run(main())
