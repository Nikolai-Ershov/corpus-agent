import os
os.environ["HF_HUB_OFFLINE"] = "1"

from index.embed import Embedder
from index.vector_store import VectorStore
from mcp.server.mcpserver import MCPServer
from index.search import search

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
    :return: a list of k dicts (chunk_id, record_id, text, score),
        sorted by descending similarity to the query
    """
    result = search(query, vector_store.chunks, k, embedder)
    return result


if __name__ == "__main__":
    mcp.run()






