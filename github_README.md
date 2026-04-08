# 📊 FinLife-OpenEnv: AI-Powered Portfolio Management

[![Validation](https://img.shields.io/badge/Validation-55%2F55%20PASS-brightgreen)](scripts/validate_submission.py)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![HF Spaces](https://img.shields.io/badge/🤗-Live%20on%20Spaces-blue)](https://huggingface.co/spaces)

Real-world **OpenEnv** environment for training AI agents on personal financial portfolio management.

---

## 🎯 Quick Facts

- ✅ **OpenEnv Spec**: Full compliance (step/reset/state + typed models)
- 💰 **Real Domain**: 95 historical stocks, 7-year market data
- 📚 **3 Progressive Tasks**: Wealth accumulation → Crisis management → Portfolio optimization
- 🤖 **Baseline Agent**: LLM-powered inference with OpenAI Client
- 🐳 **Production Ready**: Docker + HF Spaces deployment
- 🧪 **Validated**: 55/55 automated checks passing

---

## 🚀 Deployment Status

| Component | Status | Link |
|-----------|--------|------|
| API Server | ✅ Running | `http://localhost:8000` |
| Validation | ✅ 55/55 PASS | `python scripts/validate_submission.py` |
| Docker Build | ✅ Ready | `docker build -t finlife-openenv .` |
| HF Spaces | ⏳ Deploy | See DEPLOYMENT.md |

---

## 📋 What's Included

```
finlife-openenv/
├── api_server.py           # FastAPI server (step/reset/state)
├── inference.py            # LLM baseline agent with [START/STEP/END] logs
├── main.py                 # Entry point
├── requirements.txt        # All dependencies
├── Dockerfile              # Production container config
├── openenv.yaml            # Environment specification
├── .env.example            # Environment variables template
│
├── src/                    # Source code
│   ├── config.py          # Configuration
│   └── inference.py       # (moved to root for compliance)
│
├── app/                    # Core simulation logic
│   ├── environment.py     # Financial environment
│   ├── models/            # Pydantic models
│   └── logic/             # Graders and reward functions
│
├── docs/                  # Documentation
│   ├── SUBMISSION.md      # Auto-generated status
│   ├── TASKS.md          # Task specifications
│   └── STRUCTURE.md      # Project layout
│
├── scripts/               # Utilities
│   ├── validate_submission.py  # Pre-submission check
│   └── generate_submission.py  # Status generator
│
└── README.md              # This file
```

---

## 📖 Getting Started

### Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Start API server
python api_server.py

# In another terminal, test endpoints
curl -X POST http://localhost:8000/reset
curl http://localhost:8000/status
curl http://localhost:8000/tasks

# Run baseline inference
python inference.py
```

### Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` with:
```
API_BASE_URL=http://localhost:8000
MODEL_NAME=gpt-4
OPENAI_API_KEY=sk-...
HF_TOKEN=hf_...  (optional)
```

### Pre-Submission Validation

```bash
python scripts/validate_submission.py
```

Expected: **55/55 PASS** ✅

---

## 🎮 The 3 Tasks

| Task | Difficulty | Goal | Reward |
|------|-----------|------|--------|
| **Wealth Accumulation** | Easy | Build net worth over 40 years | 0.0–1.0 |
| **Crisis Management** | Medium | Preserve capital during crashes | 0.0–1.0 |
| **Portfolio Optimization** | Hard | Multi-objective (growth/risk/tax/goals) | 0.0–1.0 |

---

## 🤖 Baseline Agent

The `inference.py` script runs the LLM-powered baseline:

```
[START] task=wealth_accumulation episode=1
[STEP] task=wealth_accumulation episode=1 step=1 reward=2.50 portfolio=5000.00 regime=normal
[STEP] task=wealth_accumulation episode=1 step=2 reward=3.15 portfolio=8000.00 regime=normal
...
[END] task=wealth_accumulation episode=1 steps=60 total_reward=180.45 final_score=0.602
```

Uses OpenAI Client to make financial decisions based on:
- Current portfolio state
- Market conditions (VIX, inflation, interest rates)
- Financial goals (income, dependents, job stability)
- Tax efficiency signals

---

## 🚢 Deploy to HF Spaces

See **[DEPLOYMENT.md](DEPLOYMENT.md)** for step-by-step guide.

Quick version:
1. Push this repo to GitHub
2. Create HF Space (Docker runtime)
3. Connect GitHub repo
4. Set environment variables
5. Done! 🎉

Your Space URL will be: `https://username-finlife-openenv.hf.space`

---

## 📊 API Endpoints

### POST `/reset` - Initialize Episode
```bash
curl -X POST http://localhost:8000/reset \
  -H "Content-Type: application/json" \
  -d '{"task": "wealth_accumulation"}'
```

### POST `/step` - Execute Action
```bash
curl -X POST http://localhost:8000/step \
  -H "Content-Type: application/json" \
  -d '{
    "action": {
      "sip_amount": 500,
      "allocate_equity": 0.6,
      "allocate_debt": 0.3,
      "allocate_cash": 0.1,
      "tax_loss_harvest": false
    }
  }'
```

### GET `/status` - Health Check
```bash
curl http://localhost:8000/status
```

### GET `/state` - Current Observation
```bash
curl http://localhost:8000/state
```

### GET `/tasks` - List Available Tasks
```bash
curl http://localhost:8000/tasks
```

---

## 🏗️ Architecture

- **Framework**: FastAPI + Uvicorn
- **Environment Simulation**: Custom financial environment
- **Grading**: Task-specific graders (wealth, risk, tax optimization)
- **Baseline**: OpenAI Chat API (LLM agent)
- **Container**: Python 3.11-slim + Docker

---

## 📋 Validation Checklist

Run `python scripts/validate_submission.py`:

- ✅ File structure correct
- ✅ OpenEnv spec valid (openenv.yaml)
- ✅ All 3 tasks have graders
- ✅ API server implements all endpoints
- ✅ Dockerfile builds successfully
- ✅ Dependencies installable
- ✅ Documentation complete
- ✅ Environment variables documented

---

## 📝 License

MIT License - See LICENSE file

---

## 🔗 Links

- [OpenEnv Spec](https://github.com/pytorch/rl)
- [HF Spaces Docs](https://huggingface.co/docs/hub/spaces)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Deployment Guide](DEPLOYMENT.md)

---

**Status**: Ready for Meta PyTorch OpenEnv Hackathon Submission ✅
