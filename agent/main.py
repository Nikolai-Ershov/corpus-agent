import asyncio
import logging
import os

from dotenv import load_dotenv
from mcp import Client, StdioServerParameters
import openai

from agent.agent_loop import run_agent_turn, SYSTEM_PROMPT

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(name)s: %(message)s",
)

server_params = StdioServerParameters(
    command="C:\\Users\\nickg\\PycharmProjects\\corpus-agent\\venv\\Scripts\\python.exe",
    args=["-m", "retrieval.search_corpus"],
    cwd="C:\\Users\\nickg\\PycharmProjects\\corpus-agent",
)


async def main():
    llm_client = openai.OpenAI(
        api_key=os.environ.get("LLM_API_KEY"),
        base_url=os.environ.get("LLM_BASE_URL"),
    )

    async with Client(server_params) as mcp_client:
        tools_result = await mcp_client.list_tools()

        openai_tools = []
        for tool in tools_result.tools:
            openai_tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.input_schema,
                }
            })

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        while True:
            user_input = input("\n You: ")
            if user_input.lower() == "exit":
                break
            if not user_input.strip():
                continue

            try:
                answer = await run_agent_turn(
                    user_input, messages, llm_client, openai_tools, mcp_client
                )
            except openai.APIConnectionError:
                print("Связь с моделью прервалась. Попробуй ещё раз.")
                continue

            print(answer)


if __name__ == "__main__":
    asyncio.run(main())
