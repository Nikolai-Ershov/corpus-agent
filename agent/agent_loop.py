import json
import openai
import logging

logger = logging.getLogger(__name__)

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


async def run_agent_turn(user_text, messages, llm_client, openai_tools, mcp_client):
    messages.append({"role": "user", "content": user_text})

    while True:
        try:
            response = llm_client.chat.completions.create(
                model="gpt-5.6-luna",
                messages=messages,
                tools=openai_tools,
                reasoning_effort="none",
            )
        except openai.APIConnectionError as e:
            logger.error("LLM connection failed: %s", e)
            raise

        message = response.choices[0].message
        messages.append(message)

        if not message.tool_calls:
            return message.content
        else:
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                try:
                    tool_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError as e:
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": f"Error: failed to parse tool call arguments as JSON ({e})",
                    })
                    continue

                try:
                    result = await mcp_client.call_tool(tool_name, tool_args)
                    result_text = result.content[0].text
                except Exception as e:
                    error_detail = f"{type(e).__name__}: {e}"
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": error_detail,
                    })
                    continue

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result_text,
                })

