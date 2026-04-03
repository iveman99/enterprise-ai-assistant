import urllib.request
import json
import codecs

BASE_URL = "http://localhost:8000/api/query"

test_cases = [
    {
        "name": "1. Thanks with strong history (Checking Acknowledgment ignore history)",
        "role": "HR",
        "question": "thanks",
        "history": [
            {"role": "user", "content": "What is the dress code policy?"},
            {"role": "assistant", "content": "The dress code policy prohibits excessively revealing clothing."}
        ]
    },
    {
        "name": "2. Friendly Greeting Check",
        "role": "Finance",
        "question": "how are u",
        "history": []
    },
    {
        "name": "3. Identity/System Response Check",
        "role": "Operations",
        "question": "who build you",
        "history": []
    },
    {
        "name": "4. File Creation Out-of-Scope Bypass Check",
        "role": "Executive",
        "question": "can you make word doc for me",
        "history": []
    },
    {
        "name": "5. Farewell / Off-ramp Check",
        "role": "Legal",
        "question": "i will come back in some time",
        "history": []
    }
]

with codecs.open("test_results_v3.txt", "w", encoding="utf-8") as f:
    f.write("🚀 Starting Personality & Intent Final Verification...\n")
    f.write("=" * 60 + "\n")

    for idx, tc in enumerate(test_cases, 1):
        f.write(f"\n🧪 TEST {idx}: {tc['name']}\n")
        f.write(f"👤 Role: {tc['role']}\n")
        f.write(f"❓ Question: {tc['question']}\n")
        
        payload = {
            "question": tc["question"],
            "role": tc["role"],
            "n_results": 5,
            "conversation_history": tc["history"]
        }
        
        try:
            req = urllib.request.Request(
                BASE_URL, 
                data=json.dumps(payload).encode('utf-8'), 
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                
            f.write(f"✅ Success (HTTP 200)\n")
            f.write(f"   Intent      : {data.get('intent', 'UNKNOWN')}\n")
            f.write(f"   Chunks Used : {data.get('chunks_used')}\n")
            f.write(f"\n🤖 LLM Answer:\n")
            f.write(f"{data.get('answer')}\n")
            f.write("-" * 60 + "\n")
            
        except Exception as e:
            f.write(f"❌ Error: {e}\n")
