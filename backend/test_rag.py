# backend/test_rag.py
import sys
sys.path.append('.')
from retrieval.rag_engine import RAGEngine

engine = RAGEngine()

# Test 1 — HR question
print("\n" + "="*55)
result = engine.answer(
    question="What is the leave policy for employees?",
    role="HR"
)
print("\n📝 ANSWER:")
print(result["answer"])
print("\n📚 SOURCES:")
for s in result["sources"]:
    print(f"   • {s['filename']} ({s['department']})")

# Test 2 — Finance question
print("\n" + "="*55)
result = engine.answer(
    question="How does the budget approval process work?",
    role="Finance"
)
print("\n📝 ANSWER:")
print(result["answer"])
print("\n📚 SOURCES:")
for s in result["sources"]:
    print(f"   • {s['filename']} ({s['department']})")