"""Agent loop: runs one conversational turn, letting the model call tools
(over MCP) across multiple rounds before it returns a final plain answer."""


import json
import os
import openai
import logging

from pathlib import Path

logger = logging.getLogger(__name__)

# kept in its own file so the prompt can be edited without touching code
SYSTEM_PROMPT = (Path(__file__).parent / "system_prompt.md").read_text(encoding="utf-8")


async def run_agent_turn(user_text, messages, llm_client, openai_tools, mcp_client):
    """Send the user's message to the LLM, execute any tool calls it asks for
    via MCP, and keep looping until the LLM answers without requesting a tool —
    that plain answer is what gets returned."""
    messages.append({"role": "user", "content": user_text})
    logger.debug("USER QUESTION: %s", user_text)

    # the loop is what lets the model take several rounds of tool calls before
    # answering; it ends only via the `return` below, once there are no more
    # tool_calls left to act on
    while True:
        try:
            response = llm_client.chat.completions.create(
                model=os.environ.get("LLM_MODEL"),
                messages=messages,
                tools=openai_tools,
                reasoning_effort="none",
            )
        except openai.APIConnectionError as e:
            # this function never talks to the user directly — what the user
            # sees is decided by the caller. Logging this as a distinct
            # connection failure (not a generic exception) makes it easy to
            # spot in the logs, then re-raise so the caller can handle it
            logger.error("LLM connection failed: %s", e)
            raise

        message = response.choices[0].message
        messages.append(message)

        if not message.tool_calls:
            # no tool requested — this is the final answer, exit the loop
            logger.debug("AGENT ANSWER: %s", message.content)
            return message.content

        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            try:
                # only the argument string can fail to parse here —
                # tool_name above is a plain attribute, never risky
                tool_args = json.loads(tool_call.function.arguments)
                logger.debug("TOOL CALL: %s args=%s", tool_name, json.dumps(tool_args, ensure_ascii=False))

            except json.JSONDecodeError as e:
                # malformed JSON from the model (truncated, bad syntax) —
                # not an encoding issue. Report it back as a tool result so
                # the model can retry instead of killing the whole turn
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": f"Error: failed to parse tool call arguments as JSON ({e})",
                })
                continue  # skip this call, keep processing the rest

            try:
                result = await mcp_client.call_tool(tool_name, tool_args)
                # MCP returns one content block per list item, not a single
                # JSON array — this count is what exposed the earlier bug
                # where only content[0] was read and 9/10 chunks were
                # silently dropped whenever k=10
                logger.debug("TOOL RESULT blocks: %d", len(result.content))
                result_text = "\n".join(block.text for block in result.content)
                logger.debug("TOOL RESULT: %s", result_text)
            except Exception as e:
                # last line of defense: a bad network blip or a broken tool
                # shouldn't kill the whole conversation turn
                error_detail = f"{type(e).__name__}: {e}"
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": error_detail,
                })
                continue

            # goes back into messages with role "tool" so the model sees it
            # on the next round and can decide whether it has enough to answer
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result_text,
            })
