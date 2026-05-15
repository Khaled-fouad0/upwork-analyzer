# Upwork Job Analyzer 

A decision-support workflow for evaluating Upwork opportunities using structured signal extraction and deterministic scoring,and LLM-powered proposal writing.
---
## What It Does

Paste any Upwork job post and the system will:

1. **Extract signals** from the post (payment status, hire rate, competition, etc.)
2. **Score the opportunity** from 0 to 100 using a rule-based engine
3. **Make a decision** — Strong / Good / Weak / Reject
4. **Generate a proposal** tailored to the job — ready to send

---

## How It Works

```
Job Post (raw text)
      ↓
Signal Extraction  (LLM)
      ↓
Score Computation  (rule-based, no LLM)
      ↓
Decision Engine    (deterministic)
      ↓
Proposal Writing   (LLM)
```

The scoring logic is intentionally kept outside the LLM — deterministic rules produce consistent, auditable results.

---

## Scoring System

| Signal | Weight |
|--------|--------|
| Payment verified | +20 |
| Total spent > $10,000 | +15 |
| Hire rate ≥ 70% | +15 |
| Proposals < 10 | +10 |
| Description clarity: high | +10 |
| Description clarity: low | -10 |
| Proposals > 50 | -15 |
| Payment not verified | -20 |
| External contact requested | -20 |

| Score | Decision |
|-------|----------|
| 85–100 | ✅ Strong |
| 70–84 | 🟢 Good |
| 40–69 | 🟡 Weak |
| 0–39 | ❌ Reject |

---

## Tech Stack

- **Python** — core logic
- **Groq API** — LLM inference (llama-3.3-70b-versatile)
- **Streamlit** — web interface
- **python-dotenv** — environment management

---

## Project Structure

```
upwork-analyzer/
├── app.py          # Streamlit UI
├── analyzer.py     # Core logic — extraction, scoring, proposal
├── prompts.py      # All prompts in one place
├── .env            
├── .gitignore
└── README.md
├── LICENSE       # Open-source license(MIT)
```

---

## Getting Started

**1. Clone the repo**
```bash
git clone https://github.com/Khaled-fouad0/upwork-analyzer.git
cd upwork-analyzer
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Add your API key**

Create a `.env` file:
```
GROQ_API_KEY=your-key-here
```

Get a free key at [console.groq.com](https://console.groq.com) — no credit card required.

**4. Run**
```bash
python -m streamlit run app.py
```

---

## Why This Architecture

Most AI tools pass everything to the LLM and trust the output blindly.

This system separates concerns deliberately:

- The LLM does what it's good at — reading unstructured text and extracting meaning
- The scoring engine does what code is good at — consistent, reproducible math
- The result is a system you can audit, tune, and trust

---

## What's Next

- Structured validation using Pydantic
- Local SQLite storage for analyzed jobs
- Retry/fallback handling for malformed LLM outputs
- Caching repeated analyses
- Evaluation layer for scoring quality
- Chrome Extension
- History Log
- Multi-language

---
## 📄 License

MIT — free to use, modify, and distribute.
