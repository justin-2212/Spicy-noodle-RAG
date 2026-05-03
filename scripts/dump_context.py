import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.retrieval.langchain_rag_chain import LangChainRAGChain
from app.llm.langchain_provider import LangChainGemini

async def test_bot():
    llm = LangChainGemini().llm
    rag_chain = LangChainRAGChain(llm)
    
    query = "Khách hàng nói gì về món lẩu bò?"
    context = await rag_chain.retrieve(query)
    
    with open("context_dump.txt", "w", encoding="utf-8") as f:
        f.write(context)

if __name__ == "__main__":
    asyncio.run(test_bot())
