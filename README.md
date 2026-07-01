# Vedaz AI Astrologer — Technical Assignment

**Candidate:** Vishal Sahu
**Role:** AI Engineer — AI Astrologers, Vedaz

## 📋 Overview

This repo contains my submission for the Vedaz AI Engineer technical assessment: a review and expansion of Vedaz's AI astrologer training data (Stage 1), plus a full implementation of the tools needed to check, generate, and evaluate that data safely (Stage 2).

All responses are built around Vedaz's core principle: **compassionate, balanced, non-fatalistic guidance** that never predicts harm, redirects serious issues to professionals, and frames remedies as optional supportive practices — never guarantees.

## 📁 Structure

```
vedaz assignment/
├── README.md                  # This file
├── Stage1/                    # Dataset review & new chats — see Stage1/README.md
│   ├── README.md
│   ├── review.md               # Review of the original 15 example chats
│   ├── new_chats.jsonl         # 5 new chats written to close review gaps
└── vedaz-ai-astrologer/        # Stage 2: Chat Checker, Generator & 
    ├── README.md                # Stage 2 documentation
    ├── src/                      # All source code
    ├── data/                     # Input/output data
    ├── test_models.py            # Verifies API connection & model access
    ├── view_chats.py             # View generated conversations
    ├── setup.py
    ├── requirements.txt
    ├── .env.example
    └── .gitignore
```

## 📖 Where to Look

- **Dataset review & new example chats** → [`Stage1/README.md`](./Stage1/README.md)
- **Tooling (Chat Checker, Chat Generator, Quality Tester)** → [`vedaz-ai-astrologer/README.md`](./vedaz-ai-astrologer/README.md)

## 🚀 Quick Start

```bash
cd vedaz-ai-astrologer
pip install -r requirements.txt
cp .env.example .env   # add your GROQ_API_KEY
python test_models.py
```

See `vedaz-ai-astrologer/README.md` for full usage of each tool.

---

*Built for Vedaz's AI Engineer technical assessment.*