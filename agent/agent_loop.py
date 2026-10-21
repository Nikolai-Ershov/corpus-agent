import json
import openai
import logging

from pathlib import Path

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (Path(__file__).parent / "system_prompt.md").read_text(encoding="utf-8")


async def run_agent_turn(user_text, messages, llm_client, openai_tools, mcp_client):
    messages.append({"role": "user", "content": user_text})
    logger.debug("USER QUESTION: %s", user_text)

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
            logger.debug("AGENT ANSWER: %s", message.content)
            return message.content
        else:
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                try:
                    tool_args = json.loads(tool_call.function.arguments)
                    logger.debug("TOOL CALL: %s args=%s", tool_name, json.dumps(tool_args, ensure_ascii=False))

                except json.JSONDecodeError as e:
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": f"Error: failed to parse tool call arguments as JSON ({e})",
                    })
                    continue

                try:
                    result = await mcp_client.call_tool(tool_name, tool_args)
                    logger.debug("TOOL RESULT blocks: %d", len(result.content))
                    result_text = "\n".join(block.text for block in result.content)
                    logger.debug("TOOL RESULT: %s", result_text)
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

