import asyncio
import os
import sys

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.retrieval.langchain_rag_chain import LangChainRAGChain
from app.llm.langchain_provider import LangChainGemini

async def test_docs():
    llm = LangChainGemini().llm
    rag_chain = LangChainRAGChain(llm)
    
    query = "Khách hàng nói gì về món lẩu bò?"
    print(f"\nUser: {query}")
    
    context = await rag_chain.retrieve(query)
    print("\n--- RETRIEVED CONTEXT ---")
    print(context)

if __name__ == "__main__":
    asyncio.run(test_docs())
