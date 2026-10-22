import asyncio
import logging
import os
os.environ["HF_HUB_OFFLINE"] = "1"

from dotenv import load_dotenv
from mcp import Client, StdioServerParameters
import openai
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from agent.agent_loop import run_agent_turn, SYSTEM_PROMPT

load_dotenv()


logging.basicConfig(
    filename="tg_interface/bot.log",
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    encoding="utf-8",
)

logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)
logging.getLogger("mcp").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

server_params = StdioServerParameters(
    command="C:\\Users\\nickg\\PycharmProjects\\corpus-agent\\venv\\Scripts\\python.exe",
    args=["-m", "retrieval.search_corpus"],
    cwd="C:\\Users\\nickg\\PycharmProjects\\corpus-agent",
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Привет! Я твой личный ассистент по базе знаний. Спрашивай что угодно."
    )

MAX_MESSAGE_LENGTH = 4000


async def send_long_message(update: Update, text: str) -> None:
    """Telegram caps messages at 4096 chars — split longer answers into chunks."""
    for i in range(0, len(text), MAX_MESSAGE_LENGTH):
        await update.message.reply_text(text[i:i + MAX_MESSAGE_LENGTH])


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_text = update.message.text
    if not user_text.strip():
        return

    chat_id = update.effective_chat.id

    mcp_client = context.application.bot_data["mcp_client"]
    openai_tools = context.application.bot_data["openai_tools"]
    llm_client = context.application.bot_data["llm_client"]

    conversations = context.application.bot_data["conversations"]
    messages = conversations.setdefault(
        chat_id,
        [{"role": "system", "content": SYSTEM_PROMPT}],
    )

    try:
        answer = await run_agent_turn(
            user_text, messages, llm_client, openai_tools, mcp_client
        )
    except openai.APIConnectionError:
        await update.message.reply_text("Связь с моделью прервалась. Попробуй ещё раз.")
        return

    except Exception:
        # Intentionally broad: this is the last line of defense before
        # replying to the user — any unhandled error here must still
        # produce a reply instead of silently leaving them without an answer.
        logger.exception("Failed to handle message")
        await update.message.reply_text("Что-то пошло не так, попробуй ещё раз.")
        return

    await send_long_message(update, answer)


async def main():
    llm_client = openai.OpenAI(
        api_key=os.environ.get("LLM_API_KEY"),
        base_url=os.environ.get("LLM_BASE_URL"),
    )

    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set in .env")

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

        application = Application.builder().token(token).build()

        application.bot_data["mcp_client"] = mcp_client
        application.bot_data["openai_tools"] = openai_tools
        application.bot_data["llm_client"] = llm_client
        application.bot_data["conversations"] = {}

        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        await application.initialize()
        await application.start()
        await application.updater.start_polling()

        await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
