<div align="center">

# 🏢 Enterprise AI Knowledge Assistant

### AI-powered internal document search and Q&A system for enterprises

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org/)
[![Python](https://img.shields.io/badge/Python_3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![Vercel](https://img.shields.io/badge/Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://vercel.com/)
[![Groq](https://img.shields.io/badge/Groq-F55036?style=for-the-badge&logo=groq&logoColor=white)](https://groq.com/)

**[🌐 Live Demo](https://cryptoinfolinepoc.vercel.app)** • **[📖 API Docs](https://cryptoinfolinepoc.vercel.app/docs)** • **[📬 Contact Developer](#)**

![Enterprise AI Demo](https://img.shields.io/badge/Status-Live%20POC-brightgreen?style=for-the-badge)

</div>

---

## 📌 What Is This?

Enterprise AI Knowledge Assistant is a **Proof of Concept** built for organizations that struggle with internal document search. Instead of manually searching through hundreds of PDFs, employees simply **ask questions in plain English** and get accurate, cited answers instantly.

> 💡 **Real problem this solves:** A company with 5,000+ internal documents across departments — HR policies, Finance SOPs, IT procedures, Legal guidelines — where employees waste hours searching for information that already exists somewhere in a document.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🔍 **Semantic Search** | Finds documents by meaning, not just keywords. "Annual leave" finds "PTO policy" |
| 🔐 **Role-Based Access** | HR sees only HR docs. Finance sees only Finance docs. Executives see everything |
| 📄 **Source Citations** | Every answer shows exactly which document and department it came from |
| 💬 **Conversation Memory** | Follow-up questions are understood in context — just like talking to a person |
| ⚡ **Streaming Responses** | Answers stream word by word — fast, modern, feels like ChatGPT |
| 🚫 **Hallucination Guard** | AI refuses to answer questions not found in company documents |
| 📊 **Live Stats** | Sidebar shows documents loaded, chunks indexed, departments active |
| 🕐 **Question History** | Sidebar tracks all questions asked in the current session |

---

## 🌐 Live Demo
```
🔗 https://cryptoinfolinepoc.vercel.app
```

**Try these questions after selecting a role:**

| Role | Sample Question |
|---|---|
| HR Employee | "What is the leave policy for employees?" |
| Finance Analyst | "How does the budget approval process work?" |
| IT Engineer | "What are the cloud security management procedures?" |
| Legal Counsel | "What are the consumer protection laws?" |
| Executive | "Give me a summary of our compliance monitoring system" |

> ⚠️ **Note:** Backend runs via ngrok tunnel. Contact the developer to schedule a live demo session where the full system is active.

---

## 🏗️ System Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENT BROWSER                           │
│         https://cryptoinfolinepoc.vercel.app                │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTPS
┌─────────────────────▼───────────────────────────────────────┐
│                  REACT FRONTEND (Vercel)                     │
│   Header │ Role Switcher │ Chat UI │ Citations │ Sidebar     │
└─────────────────────┬───────────────────────────────────────┘
                      │ REST API / SSE Stream
┌─────────────────────▼───────────────────────────────────────┐
│               FASTAPI BACKEND (ngrok tunnel)                 │
│         /api/query │ /api/stream │ /api/health               │
│         /api/stats │ /api/roles  │ /api/departments          │
└──────┬──────────────────────────────────┬───────────────────┘
       │                                  │
┌──────▼──────────┐              ┌────────▼────────┐
│   RAG ENGINE    │              │  VECTOR STORE   │
│                 │              │                 │
│ 1. Retrieve     │◄─────────────│ ChromaDB        │
│ 2. Filter RBAC  │              │ 1,193 chunks    │
│ 3. Build prompt │              │ all-MiniLM-L6   │
│ 4. Stream Groq  │              │ embeddings      │
└──────┬──────────┘              └─────────────────┘
       │
┌──────▼──────────┐
│   GROQ LLM      │
│ llama-3.1-8b    │
│ < 2s response   │
└─────────────────┘
```

---

## 📊 POC Statistics

<div align="center">

| Metric | Value |
|---|---|
| 📁 Departments | 5 |
| 📄 Documents Indexed | 42 PDFs |
| 🔍 Searchable Chunks | 1,193 |
| ⚡ Avg Response Time | < 3 seconds |
| 🧠 Embedding Model | all-MiniLM-L6-v2 (local) |
| 🤖 LLM | Groq llama-3.1-8b-instant |
| 💰 Infrastructure Cost | $0 (fully free tier) |

</div>

---

## 🔐 Role-Based Access Control (RBAC)
```
┌─────────────────┬─────────────────────────────────────┐
│ Role            │ Department Access                    │
├─────────────────┼─────────────────────────────────────┤
│ HR Employee     │ HR                                  │
│ Finance Analyst │ Finance                             │
│ IT Engineer     │ IT                                  │
│ Legal Counsel   │ Legal                               │
│ Ops Manager     │ Operations                          │
│ HR Manager      │ HR + Operations                     │
│ Finance Manager │ Finance + Legal                     │
│ Executive       │ HR + Finance + IT + Legal + Ops     │
└─────────────────┴─────────────────────────────────────┘
```

When a Finance employee asks about HR policies — they get zero results.
When an Executive asks anything — they get answers from all departments.
**This is demonstrated live in the POC.**

---

## 🧠 Tech Stack

### Backend
| Technology | Purpose | Version |
|---|---|---|
| Python | Core language | 3.11 |
| FastAPI | REST API framework | Latest |
| Uvicorn | ASGI server | Latest |
| PyMuPDF (fitz) | PDF text extraction | Latest |
| LangChain | RAG orchestration | 0.2.16 |
| sentence-transformers | Local embeddings | Latest |
| ChromaDB | Vector database | 0.5.3 |
| Groq SDK | LLM API client | Latest |

### Frontend
| Technology | Purpose | Version |
|---|---|---|
| React | UI framework | 18 |
| Vite | Build tool | Latest |
| Axios | API calls | Latest |
| react-markdown | Render AI answers | Latest |
| lucide-react | Icons | Latest |

### Infrastructure
| Service | Purpose | Cost |
|---|---|---|
| Vercel | Frontend hosting | Free |
| ngrok | Backend tunnel | Free |
| Groq | LLM inference | Free tier |
| GitHub | Version control | Free |

---

## 📁 Project Structure
```
enterprise-ai-assistant/
│
├── 📁 backend/
│   ├── 📁 ingestion/
│   │   ├── pdf_reader.py         # Stage 1: PDF → raw text (PyMuPDF)
│   │   ├── chunker.py            # Stage 2: Text → 500-char chunks
│   │   ├── vector_store.py       # Stage 3+4: Chunks → vectors → ChromaDB
│   │   └── ingest.py             # Master pipeline runner
│   │
│   ├── 📁 retrieval/
│   │   ├── retriever.py          # Semantic search + RBAC department filter
│   │   └── rag_engine.py         # RAG pipeline — retrieve → prompt → Groq
│   │
│   ├── 📁 api/
│   │   └── routes.py             # All FastAPI endpoints
│   │
│   ├── 📁 models/
│   │   └── schemas.py            # Pydantic request/response schemas
│   │
│   ├── 📁 core/
│   │   └── config.py             # Centralised config from .env
│   │
│   ├── main.py                   # FastAPI app entry point
│   └── requirements.txt          # Python dependencies
│
├── 📁 frontend/
│   └── 📁 src/
│       ├── 📁 components/
│       │   ├── Header.jsx         # App bar + role switcher dropdown
│       │   ├── Sidebar.jsx        # System stats + question history
│       │   ├── MessageBubble.jsx  # Chat message + typing animation
│       │   ├── SourceCards.jsx    # Citation cards below each answer
│       │   └── InputBar.jsx       # Question input + send button
│       │
│       ├── 📁 services/
│       │   └── api.js             # All API calls + streaming logic
│       │
│       ├── App.jsx                # Root component + state management
│       ├── index.css              # Global styles + CSS variables
│       └── main.jsx               # React entry point
│
├── 📁 documents/
│   ├── 📁 HR/          (8 documents)
│   ├── 📁 Finance/     (8 documents)
│   ├── 📁 IT/          (10 documents)
│   ├── 📁 Legal/       (7 documents)
│   └── 📁 Operations/  (9 documents)
│
├── .env                           # API keys — never committed
├── .gitignore
├── docker-compose.yml
└── README.md
```

---

## 🔄 How the Ingestion Pipeline Works
```
Step 1 — READ
  PyMuPDF opens each PDF
  Extracts raw text page by page
  Labels each doc with its department

Step 2 — CHUNK
  LangChain splits text into 500-character chunks
  50-character overlap between chunks
  Preserves context at boundaries

Step 3 — EMBED
  sentence-transformers converts each chunk to a 384-dimensional vector
  Runs locally — no API calls, no rate limits, no cost

Step 4 — STORE
  ChromaDB stores vectors + original text + metadata
  Metadata includes: department, filename, chunk index
  Persisted to disk — survives restarts
```

**Result:** 42 documents → 1,193 searchable chunks → stored in ChromaDB

---

## 🔄 How a Query Works
```
User: "What is the leave policy?" (Role: HR Employee)
              ↓
1. Convert question to vector using same embedding model
              ↓
2. Search ChromaDB for top 5 closest vectors
   WHERE department = "HR"  ← RBAC filter applied here
              ↓
3. Retrieved chunks:
   [0.733] Leave Policy Template.pdf — chunk 3
   [0.674] Leave Policy Template.pdf — chunk 7
   [0.606] Employee Exit Policy Template.pdf — chunk 2
              ↓
4. Build prompt:
   "Here are excerpts from HR documents: [chunks]
    Answer this question using ONLY these documents:
    What is the leave policy?"
              ↓
5. Stream to Groq llama-3.1-8b-instant
              ↓
6. Return: answer + source citations + match scores
```

---

## 🚀 Running Locally

### Prerequisites

- Python 3.11 (specifically — not 3.12, 3.13, or 3.14)
- Node.js 20+
- Groq API key — free at [console.groq.com](https://console.groq.com)

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/enterprise-ai-assistant.git
cd enterprise-ai-assistant
```

### 2. Backend setup
```bash
# Create virtual environment with Python 3.11
py -3.11 -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements.txt
```

### 3. Environment variables

Create a `.env` file in the root folder:
```env
# LLM
GROQ_API_KEY=your_groq_key_here
GEMINI_API_KEY=your_gemini_key_here

# App
APP_NAME="Enterprise AI Knowledge Assistant"
APP_VERSION="1.0.0"
ENVIRONMENT=development

# Vector Store
CHROMA_DB_PATH=./chroma_db
COLLECTION_NAME=enterprise_docs

# Documents
DOCUMENTS_PATH=../documents
CHUNK_SIZE=500
CHUNK_OVERLAP=50

# Server
API_HOST=0.0.0.0
API_PORT=8000
```

### 4. Run ingestion pipeline
```bash
# From backend/ folder
python -m ingestion.ingest
```

This reads all PDFs, creates chunks, generates embeddings and stores everything in ChromaDB. Run once — data persists.

### 5. Start the backend
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API docs available at: `http://localhost:8000/docs`

### 6. Start the frontend
```bash
cd ../frontend
npm install
npm run dev
```

Open: `http://localhost:5173`

---

## 🌍 Deployment

### Frontend — Vercel
```bash
# Push to GitHub — Vercel auto-deploys
git push origin main
```

### Backend — ngrok (for POC demos)
```bash
# Terminal 1 — run backend
uvicorn main:app --host 0.0.0.0 --port 8000

# Terminal 2 — expose via ngrok
ngrok http 8000
```

Update `frontend/src/services/api.js` with the ngrok URL, then push to trigger Vercel redeploy.

---

## 🔑 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Health check |
| GET | `/api/stats` | Vector store statistics |
| GET | `/api/departments` | List all departments |
| GET | `/api/roles` | List roles and their access |
| POST | `/api/query` | Ask a question (full response) |
| POST | `/api/stream` | Ask a question (streaming SSE) |

### Example Request
```bash
curl -X POST https://your-backend/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the leave policy?",
    "role": "HR",
    "n_results": 5,
    "conversation_history": []
  }'
```

### Example Response
```json
{
  "answer": "According to the Leave Policy Template (Source 1), employees are entitled to Privilege Leave, Casual Leave, Sick Leave, Maternity Leave, Paternity Leave, and Sabbatical Leave...",
  "sources": [
    {
      "filename": "Leave Policy Template.pdf",
      "department": "HR",
      "score": 0.733
    }
  ],
  "role": "HR",
  "chunks_used": 5,
  "question": "What is the leave policy?"
}
```

---

## 🗺️ Production Roadmap

This is a POC. The production version will include:

- [ ] **SharePoint Connector** — Microsoft Graph API auto-sync
- [ ] **Azure Active Directory** — SSO authentication
- [ ] **Pinecone / Weaviate** — scalable managed vector database
- [ ] **Document Auto-Classification** — AI tags unsorted documents by department
- [ ] **Admin Dashboard** — usage analytics, query logs, performance metrics
- [ ] **Multi-language Support** — answer in employee's preferred language
- [ ] **Document Upload UI** — drag and drop new documents
- [ ] **Audit Trail** — log every query for compliance
- [ ] **Mobile App** — React Native version

---

## 💡 Why This Approach

### Why RAG instead of fine-tuning?

Fine-tuning an LLM on company documents is expensive, slow to update, and can hallucinate confidently. RAG (Retrieval Augmented Generation) retrieves actual document text as context — answers are always grounded in real documents and update instantly when documents change.

### Why local embeddings?

Gemini/OpenAI embedding APIs have rate limits, costs, and latency. The `all-MiniLM-L6-v2` model runs locally — zero API calls, zero cost, no rate limits, works offline.

### Why Groq?

Groq's custom LPU hardware delivers LLM inference 10-20x faster than traditional GPUs. `llama-3.1-8b-instant` on Groq typically responds in under 1 second — making streaming feel instant.

---

## 👨‍💻 Developer

**Veman S Chippa**

Built as a POC to demonstrate enterprise AI capabilities for internal knowledge management systems.

---

## 📄 License

This project is proprietary and built for client demonstration purposes. All rights reserved.

---

<div align="center">

**Built with ❤️ to solve real enterprise knowledge management problems**

⭐ Star this repo if you found it useful

</div>
