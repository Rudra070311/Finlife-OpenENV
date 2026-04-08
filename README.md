---
title: FinLife-OpenEnv
emoji: 💰
colorFrom: blue
colorTo: green
sdk: docker
pinned: true
---

# FinLife-OpenEnv: Real-World Portfolio Management

A complete OpenEnv environment for training AI agents on personal financial portfolio management.

## Features

- **3 Progressive Tasks** (easy → hard)
- **95 Real Stocks** with 7-year historical data
- **4 Market Regimes** with realistic volatility
- **Full OpenEnv Spec** compliance
- **LLM-Powered Baseline** agent
- **Production Ready** with Docker

## Tasks & Grading Rubric

### Task 1: Wealth Accumulation (Easy)
Build wealth over time with balanced strategy
- Grading: Net worth (+60%), Savings maintenance (+20%), Portfolio growth (+20%)
- Baseline score: 0.50+

### Task 2: Crisis Management (Medium)
Preserve capital during market crashes
- Grading: Capital preservation (+50%), Diversification (+20%), Recovery (+20%), Tax optimization (+10%)
- Baseline score: 0.50+

### Task 3: Portfolio Optimization (Hard)
Multi-objective optimization under constraints
- Grading: Wealth accumulation (+30%), Risk-adjusted returns (+25%), Tax efficiency (+20%), Goal achievement (+15%), Diversification (+10%)
- Baseline score: 0.50+

All tasks scored 0.0-1.0 range.

## Quick Start

\\\ash
pip install -r requirements.txt
python main.py
\\\

Server runs on http://localhost:8000

## Environment Variables

- **API_BASE_URL**: Server endpoint (default: http://localhost:8000)
- **MODEL_NAME**: LLM model (default: gpt-4)
- **OPENAI_API_KEY**: API authentication key
- **HF_TOKEN**: Hugging Face token (optional)

## Project Structure

`
finlife-openenv/
├── ROOT LEVEL (essentials)
│   ├── main.py
│   ├── api_server.py
│   ├── requirements.txt
│   └── Dockerfile
├── src/               # Source code
├── docs/              # Documentation
└── scripts/           # Utilities
`

---

See docs/SUBMISSION.md for complete details.