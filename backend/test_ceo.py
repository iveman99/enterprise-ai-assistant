import urllib.request
import json
import codecs

BASE_URL = "http://localhost:8000/api/query"

test_cases = [
    {
        "name": "1. Multi-Department Strategic Query",
        "role": "Executive",
        "question": "Summarize our IT security password policies and HR exit policies.",
        "history": []
    },
    {
        "name": "2. Global Summarization Request",
        "role": "Executive",
        "question": "Summarize all company policies for me.",
        "history": []
    },
    {
        "name": "3. Executive 'Write this for me' check",
        "role": "Executive",
        "question": "Write an email draft to the board about the budget.",
        "history": []
    },
    {
        "name": "4. Impatient Frustration Check",
        "role": "Executive",
        "question": "this is useless what do you actually do",
        "history": [
            {"role": "user", "content": "What is the dress code?"},
            {"role": "assistant", "content": "The dress code covers..."}
        ]
    }
]

with codecs.open("test_ceo.txt", "w", encoding="utf-8") as f:
    f.write("🚀 Starting CEO-Level Verification...\n")
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
