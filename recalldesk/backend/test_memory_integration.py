import asyncio
import os
from app.hindsight import manager
import datetime

async def test():
    print("Testing Hindsight Memory Integration...")
    # Initialize real hindsight server
    success = await manager.init_hindsight(
        llm_provider="openai",
        llm_model="gpt-4o-mini",
        llm_api_key="sk-fake",
        embedded=True,
        embeddings_provider="openai",
        reranker_provider="rrf",
    )
    print("Init Success:", success)
    print("Status:", manager.get_status())
    
    if not success:
        print("Falling back, using mock")
        
    customer = "test-cust-1"
    
    print("\n--- Creating Bank ---")
    res = manager.create_bank(customer, "Test User")
    print(res)
    
    print("\n--- Retaining Memory ---")
    res = manager.retain(
        customer,
        "Customer tried cache clearing, it failed. Updating billing profile worked.",
        context="test_context",
        metadata={"outcome": "resolved"}
    )
    print(res)
    
    print("\n--- Recalling Memory ---")
    res = manager.recall(customer, "billing failed cache clearing")
    print("Recall Results:", res["count"])
    for i, mem in enumerate(res.get("memories", [])):
        print(f"{i+1}. {mem['text']} (Score: {mem.get('score', 0)})")
        
    print("\n--- Testing Isolation ---")
    customer2 = "test-cust-2"
    manager.create_bank(customer2, "Another User")
    res2 = manager.recall(customer2, "billing failed cache clearing")
    print("Recall Results for Customer 2:", res2["count"])

if __name__ == "__main__":
    asyncio.run(test())
