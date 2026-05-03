import asyncio
import os
import sys
import io

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set encoding for Windows terminal
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import langchain
langchain.verbose = False
langchain.debug = False
langchain.llm_cache = None

from app.retrieval.langchain_rag_chain import LangChainRAGChain
from app.llm.langchain_provider import LangChainGroq

async def test_bot():
    llm = LangChainGroq().llm
    rag_chain = LangChainRAGChain(llm)
    
    query = "Combo Cặp Đôi có những gì?"
    print(f"User: {query}")
    answer = await rag_chain.generate(query)
    print(f"Bot: {answer}")

if __name__ == "__main__":
    asyncio.run(test_bot())
