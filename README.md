# NEXUS DEBATE — AI Debate Arena 🎙️⚡

> **Two AI agents argue. A judge decides. You watch it unfold.**

A production-grade multi-agent debate system where two specialized AI agents argue opposing sides of any topic, and a third judge agent analyzes both arguments and delivers a verdict — all in real time, with optional voice input and output.

**Live Demo:** [sunny-shortbread-273f53.netlify.app](https://sunny-shortbread-273f53.netlify.app)

---

## What It Does

You give a topic. Two agents fight over it. A judge picks a winner.

The PRO agent argues FOR the topic. The CON agent argues AGAINST it. Both run **simultaneously** using LangGraph's parallel fan-out pattern. Once both finish, the Judge agent reads both arguments and delivers a structured verdict with reasoning.

```
Topic: "Messi vs Ronaldo"
        ↓
┌─────────────────────────────────────┐
│         LangGraph Fan-Out           │
│                                     │
│  PRO Agent ──────────┐              │
│  (argues FOR)        ├──→ Judge ──→ Verdict
│  CON Agent ──────────┘              │
│  (argues AGAINST)                   │
└─────────────────────────────────────┘
        ↓
   PRO WINS / CON WINS + Reasoning
```

---

## Architecture

This project introduces the **parallel multi-agent pattern** — both debater agents run simultaneously on the same input, unlike sequential pipelines.

| Layer | Technology | Role |
|---|---|---|
| PRO Debater | Groq LLaMA 3.3 70B | Argues FOR the topic |
| CON Debater | Groq LLaMA 3.3 70B | Argues AGAINST the topic |
| Judge | Groq LLaMA 3.3 70B | Reads both args, picks winner |
| Orchestration | LangGraph `Send` API | Parallel fan-out/fan-in |
| Memory | LangGraph MemorySaver | Per-session conversation state |
| STT | Groq Whisper (`whisper-large-v3`) | Voice input → text |
| TTS | gTTS | Winner verdict → spoken audio |
| API | FastAPI | `/debate` and `/voice-debate` endpoints |
| Frontend | Vanilla HTML/CSS/JS | Futuristic dual-card UI |
| Backend | Render | Python 3.11.8, auto-deploys on push |
| Frontend | Netlify | Static deploy |

---

## The Key Pattern — Parallel Fan-Out with `Send`

This is the core architectural difference from a standard sequential agent pipeline.

```python
from langgraph.types import Send

def fan_out(state: State):
    return [
        Send("debater_pro", state),  # fires simultaneously
        Send("debater_con", state)   # fires simultaneously
    ]

builder.add_conditional_edges(START, fan_out)
builder.add_edge("debater_pro", "judge")  # judge waits for both
builder.add_edge("debater_con", "judge")  # judge waits for both
```

Both debaters receive the same state and run in parallel. LangGraph waits for both to complete before the judge node fires. This cuts latency roughly in half compared to running them sequentially.

---

## Endpoints

### `GET /`
Health check.
```json
{ "message": "Debate_agent is running" }
```

### `POST /debate`
Text-based debate.
```json
// Request
{ "topic": "Messi vs Ronaldo", "session_id": "abc123" }

// Response
{
  "pros": "Messi has 8 Ballon d'Or awards...",
  "con": "Ronaldo has dominated multiple leagues...",
  "winner": "PRO",
  "reasoning": "The PRO argument presents a more compelling case because..."
}
```

### `POST /voice-debate`
Voice-based debate. Accepts multipart/form-data.
```
audio      → audio file (webm/m4a)
session_id → string
```
Returns JSON with `pros`, `con`, `winner`, `reasoning` + `audio` (base64 MP3 of the verdict).

---

## Tech Stack

- **LangGraph** — parallel multi-agent orchestration via `Send` API
- **LangChain** — LLM integrations and message handling
- **Groq** — blazing fast LLaMA 3.3 70B inference + Whisper STT
- **FastAPI** — async Python API
- **gTTS** — text-to-speech for the judge's verdict
- **MemorySaver** — in-memory checkpointing per session
- **Render** — backend deployment
- **Netlify** — frontend deployment

---

## Project Structure

```
Debate_agent/
├── api.py           # FastAPI — /debate and /voice-debate endpoints
├── graph.py         # LangGraph StateGraph — parallel fan-out/fan-in
├── agents.py        # debater_pro, debater_con, judge agent functions
├── state.py         # Shared state schema (TypedDict)
├── requirements.txt
└── runtime.txt      # Python 3.11.8
```

---

## State Schema

```python
class State(TypedDict):
    messages:  Annotated[Sequence[AnyMessage], add_messages]
    topic:     str   # debate topic
    pros:      str   # PRO agent's argument
    cons:      str   # CON agent's argument
    winner:    str   # "PRO" or "CON"
    reasoning: str   # judge's explanation
```

---

## Local Setup

**1. Clone the repo**
```bash
git clone https://github.com/MAGUIRE-GOATED/Debate_agent.git
cd Debate_agent
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Set up environment variables**
```bash
# .env
GROQ_API_KEY=your_groq_key
```

**4. Run the server**
```bash
uvicorn api:app --reload
```

**5. Test at** `http://127.0.0.1:8000/docs`

---

## Deployment

**Backend (Render)**
- Build: `pip install -r requirements.txt`
- Start: `uvicorn api:app --host 0.0.0.0 --port 10000`
- Env vars: `GROQ_API_KEY`

**Frontend (Netlify)**
- Drag and drop `index.html`
- Update `API_BASE` in the HTML to your Render URL

---

## How The Judge Works

The judge receives both arguments and responds in strict JSON format:

```python
system_prompt = """Respond ONLY with a JSON object:
{
    "winner": "PRO" or "CON",
    "reasoning": "2-3 sentence explanation"
}"""
```

Structured output keeps the response predictable and parseable — no hallucinated formatting, no extra text.

---

## Related Projects

- [Voice Sports Agent](https://github.com/MAGUIRE-GOATED/Voice_agent) — voice-powered sports research agent with Groq Whisper + gTTS
- [Sports Agent](https://github.com/MAGUIRE-GOATED/SPORTS_AGENT) — hierarchical multi-agent sports researcher with Tavily
- [Flight Agent](https://github.com/MAGUIRE-GOATED/Flight_agent) — RAG over KLM baggage docs with BM25 + ChromaDB

---

Built by [Wali](https://github.com/MAGUIRE-GOATED) — first-year CS student at IIIT Delhi, building production AI agents.
