import asyncio
import os
import sys
import io
import time

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
from app.utils.logger import logger

# Test cases: (query, relevant_ids)
TEST_SET = [
    ("Mì kim chi hải sản giá bao nhiêu?", [1]),
    ("Lẩu nào đắt nhất quán?", [8]),
    ("Combo sinh viên gồm những gì?", [19]),
    ("Mì trộn gà giòn", [22]),
    ("Trà sữa trân châu đường đen", [16]),
    ("Lẩu tomyum bò", [8]),
    ("Mì bạch tuộc", [5]),
    ("Kimbap chiên", [11]),
    ("Tokbokki phô mai", [13]),
    ("Trà đào cam sả", [15]),
]

async def evaluate():
    logger.info("Starting Retrieval Evaluation...")
    
    # Initialize RAG chain
    llm = LangChainGroq().llm
    rag_chain = LangChainRAGChain(llm)
    retriever = rag_chain.base_retriever
    
    k_values = [1, 3, 5, 10]
    results = {k: {"precision": 0, "recall": 0} for k in k_values}
    
    total_queries = len(TEST_SET)
    
    for query, relevant_ids in TEST_SET:
        print(f"\nQuery: {query}")
        
        # Get documents
        # We need to call _get_relevant_documents or use invoke
        # Since _get_relevant_documents is protected, we use invoke
        docs = retriever.invoke(query)
        
        # Extract product IDs from metadata
        # In our builder, we stored 'product_id' or 'original_id' (for chunks)
        retrieved_ids = []
        for doc in docs:
            pid = doc.metadata.get("original_id") or doc.metadata.get("product_id")
            if pid and pid not in retrieved_ids:
                retrieved_ids.append(pid)
        
        print(f"  Retrieved IDs: {retrieved_ids[:10]}...")
        
        for k in k_values:
            top_k_retrieved = retrieved_ids[:k]
            hits = len(set(top_k_retrieved) & set(relevant_ids))
            
            precision = hits / k if k > 0 else 0
            recall = hits / len(relevant_ids) if len(relevant_ids) > 0 else 0
            
            results[k]["precision"] += precision
            results[k]["recall"] += recall
            
    # Calculate averages
    print("\n" + "="*40)
    print("AVERAGE METRICS")
    print("="*40)
    for k in k_values:
        avg_p = results[k]["precision"] / total_queries
        avg_r = results[k]["recall"] / total_queries
        print(f"K={k}: Precision: {avg_p:.4f} | Recall: {avg_r:.4f}")
    print("="*40)

if __name__ == "__main__":
    asyncio.run(evaluate())
