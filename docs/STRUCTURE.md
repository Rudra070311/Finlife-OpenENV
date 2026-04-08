# Project Structure

\\\
finlife-openenv/
├── api_server.py              # FastAPI + OpenEnv endpoints
├── main.py                    # Launcher
├── inference.py               # Baseline agent (LLM-powered)
├── config.py                  # Settings
├── requirements.txt           # Dependencies
├── openenv.yaml               # OpenEnv specification
├── Dockerfile                 # Container config
├── README.md                  # Quick start
├── SUBMISSION.md              # Full submission details (auto-generated)
│
├── app/                       # Application logic
│   ├── environment.py         # Simulation core
│   ├── reward.py              # Reward computation
│   └── logic/
│       ├── environment_enhanced.py
│       ├── graders/finlife_graders.py
│       └── validation/models.py
│
├── tests/                     # Unit tests
├── data/                      # Market data (95 stocks, 7 years)
└── episode_outputs/           # Results & traces
\\\