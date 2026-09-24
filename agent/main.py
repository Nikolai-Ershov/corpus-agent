import asyncio
import json
import os
from dotenv import load_dotenv
from mcp import Client, StdioServerParameters
from openai import OpenAI

SYSTEM_PROMPT = """
    You are the user's personal assistant, living and thinking entirely
    within their personal knowledge base, accessed through a search tool.
    This knowledge base is all you know — your only source of facts and
    opinions. You answer like someone who has read and internalized this
    material, not like a search engine returning results.
    
    Your job is to help the user navigate their knowledge base: find the
    information relevant to their question, and answer based on it.
    
    Rules:
    - Use only information from the knowledge base. Do not draw on general
      knowledge as a source of facts.
    - Don't just list what you found — draw conclusions, connect ideas
      across entries, and answer as your own understanding, not as a
      list of quotes.
    - If there's no exact answer in the knowledge base but something
      relevant exists, say plainly that you didn't find an exact answer,
      and offer the relevant material instead.
    - If there's no exact answer in the knowledge base, actively reason about
      what relates to the question, even indirectly — don't require a literal
      topical match. If you find something that connects, say plainly you
      didn't find an exact answer, then reason from what you found and offer
      it as the closest available answer.
    - Mention the source (which note or record) only if the user
      explicitly asks for it.
    
    Above all: synthesize and reason from what you find — you are not a
    search engine, you are the user's own understanding of their material.
"""

load_dotenv()
llm_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

server_params = StdioServerParameters(
    command="C:\\Users\\nickg\\PycharmProjects\\corpus-agent\\venv\\Scripts\\python.exe",
    args=["-m", "retrieval.search_corpus"],
    cwd="C:\\Users\\nickg\\PycharmProjects\\corpus-agent",
)


async def main():
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

            messages.append({
                "role": "user",
                "content": user_input
            })

            while True:

                response = llm_client.chat.completions.create(
                    model="gpt-5.6-luna",
                    messages=messages,
                    tools=openai_tools,
                    reasoning_effort="none",
                )

                print(response)

                message = response.choices[0].message
                messages.append(message)

                if not message.tool_calls:
                    print(message.content)
                    break
                else:
                    for tool_call in message.tool_calls:
                        tool_name = tool_call.function.name
                        tool_args = json.loads(tool_call.function.arguments)

                        result = await mcp_client.call_tool(tool_name, tool_args)
                        result_text = result.content[0].text

                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": result_text,
                        })

if __name__ == "__main__":
    asyncio.run(main())


