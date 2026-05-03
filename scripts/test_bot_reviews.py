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
    
    chat_history = []
    for query in [
        "Khách hàng nói gì về món lẩu bò?",
        "Khách hàng đánh giá sao về món lẩu bò"
    ]:
        print(f"\nUser: {query}")
        answer = await rag_chain.generate(query, chat_history=chat_history)
        print(f"Bot: {answer}")
        
        # Update history
        from langchain_core.messages import HumanMessage, AIMessage
        chat_history.extend([
            HumanMessage(content=query),
            AIMessage(content=answer)
        ])

if __name__ == "__main__":
    asyncio.run(test_bot())
