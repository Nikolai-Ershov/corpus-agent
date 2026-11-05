"""MCP server: exposes search_corpus as a tool the agent can call over MCP.
Spawned as its own subprocess by telegram_bot.py / agent/main.py."""

import os
import logging

# must come before the Embedder import below — it pulls in huggingface_hub
os.environ["HF_HUB_OFFLINE"] = "1"

from index.embed import Embedder
from index.vector_store import VectorStore
from mcp.server.mcpserver import MCPServer
from index.search import search

# stderr, not stdout — stdout is reserved for the MCP protocol itself
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(name)s: %(message)s",
)

embedder = Embedder()
vector_store = VectorStore()
vector_store.load("data/corpus_index.json")
mcp = MCPServer("corpus-agent")


@mcp.tool()
def search_corpus(query: str, k: int = 3):
    """Searches for semantically relevant fragments in the user's personal notes.

    Always use this when the user asks to find, recall, or clarify any
    information from their notes — the agent should rely exclusively on
    this knowledge base, not on general/external knowledge.

    :param query: the user's question or topic to search for
    :param k: how many of the most relevant fragments to return
    :return: a list of k dicts (chunk_id, origin_ref, text, score),
        sorted by descending similarity to the query
    """
    # sent straight to the LLM as the tool description — a prompt, not just docs

    if not vector_store.chunks:
        raise RuntimeError("Knowledge base failed to load and is currently empty.")  # load() degrades silently to [] — this is where that becomes loud

    result = search(query, vector_store.chunks, k, embedder)
    return result


if __name__ == "__main__":
    mcp.run()
