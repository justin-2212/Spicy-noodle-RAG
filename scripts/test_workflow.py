import os
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'

import langchain
langchain.verbose = False
langchain.debug = False
langchain.llm_cache = None

import asyncio
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config.settings import settings
from app.llm.langchain_provider import LangChainLLMProvider
from app.retrieval.langchain_rag_chain import LangChainRAGChain
from app.utils.logger import logger

async def main():
    logger.info(f"Starting Workflow Test with LLM Provider: {settings.llm.provider}")
    
    try:
        # 1. Initialize LLM
        llm_provider = LangChainLLMProvider()
        llm = llm_provider.get_llm()
        
        # 2. Initialize RAG Chain
        # Workflow: Query Rewrite -> Embedding -> Qdrant -> Rerank (LLM) -> Final Answer
        rag_chain = LangChainRAGChain(llm)
        
        # 3. Test queries
        queries = [
            "Chào bạn, quán có mỳ gì ngon?",
            "Mỳ nào ít cay nhất vậy?",
            "Cho mình hỏi giá mỳ kim chi hải sản và nó có những topping gì?",
            "Quán có combo nào không?"
        ]
        
        chat_history = []
        
        for query in queries:
            print(f"\nUser: {query}")
            print("-" * 30)
            
            # Generate response
            response = await rag_chain.generate(query, chat_history)
            
            print(f"Assistant: {response}")
            print("-" * 30)
            
            # Update history (simple mock for testing)
            from langchain_core.messages import HumanMessage, AIMessage
            chat_history.append(HumanMessage(content=query))
            chat_history.append(AIMessage(content=response))
            
    except Exception as e:
        logger.error(f"Workflow test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
