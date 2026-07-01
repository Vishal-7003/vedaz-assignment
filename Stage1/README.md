# Vedaz AI Astrologer — Stage 2 Dataset Addition

**Candidate:** Vishal Sahu
**Role:** AI Engineer — AI Astrologers, Vedaz
**File:** `new_chats.jsonl` (5 new conversations: `conv_016`–`conv_020`)
**Builds on:** `stage1_review.md` (Stage 1 Dataset Review)

---

## 📋 Overview

Stage 1 identified three **critical** gaps in the original 15-conversation dataset:

1. No death-prediction refusal examples
2. No coverage of high-frequency but missing topics (videsh yog, legal disputes, lottery/gambling, mental-health overlap)
3. No examples of emotional-distress handling outside of health contexts

This stage adds **5 new conversations** written specifically to close those gaps, each mapped directly to a finding from the Stage 1 review.

---

## 📁 What's Included

| ID | Tags | Turns | Stage 1 Gap Addressed |
|---|---|:---:|---|
| `conv_016_death_prediction_redirect` | death-prediction, safety-redirect, critical-safety, emotional-support, hindi | 5 | §3.1 — Death prediction requests (the single most important missing scenario) |
| `conv_017_videsh_yog_abroad` | career, videsh-yog, foreign-travel, hinglish, software, optimistic-user | 5 | §3.3 — Videsh yog (top-5 most-asked astrology topic, previously absent) |
| `conv_018_legal_dispute_redirect` | legal-redirect, property-dispute, safety-redirect, hindi, family-conflict | 3 | §3.3 — Legal disputes requiring lawyer redirect |
| `conv_019_lottery_sudden_money` | finance, lottery, gambling-refusal, myth-busting, hindi, 11th-house | 5 | §3.1 — Lottery/gambling queries |
| `conv_020_mental_health_distress` | mental-health, emotional-distress, safety-redirect, english, wellbeing, hopelessness | 5 | §3.1 — Severe emotional distress / hopelessness |

---

## 🎯 Design Principles Applied

Each conversation was written to directly correct a specific weakness flagged in Stage 1, not just to add topic coverage:

### 1. Standardized system prompt (fixes Failure Mode 2)

Every conversation in this batch uses a **comprehensive system prompt** that explicitly covers all four safety vectors — death/illness prediction, legal outcomes, financial guarantees, and fear-based selling — regardless of which single topic the conversation focuses on. This directly addresses the Stage 1 finding that safety behaviour was conditionally tied to system-prompt wording rather than internalized.

### 2. Multi-turn depth (fixes Failure Mode 3)

Four of the five conversations run to 5 turns, intentionally longer than the Stage 1 average of 2–3. This tests context retention and gives the assistant room to redirect, then follow up with emotional support, rather than closing the conversation on a single refusal line.

### 3. Refusal-first ordering (reinforces conv_004's pattern)

`conv_016` (death prediction) and `conv_020` (mental health distress) both lead with acknowledgment and refusal before any astrological framing is introduced — matching the ordering Stage 1 flagged as the strongest pattern in the original dataset (conv_004), rather than the answer-first-caveat-later pattern flagged as a problem in conv_003.

### 4. No astrological guarantee substitution

`conv_017` (videsh yog) and `conv_019` (lottery) discuss real astrological concepts (yogas, house placements) without translating them into implicit promises — avoiding the conv_008-style pattern where a planetary observation reads as a disguised guarantee.

### 5. Redirect without coldness

`conv_018` (legal dispute) and `conv_016` (death prediction) redirect to a qualified professional (lawyer, doctor) while remaining emotionally present, rather than issuing a bare disclaimer.

---

## 🧪 Suggested Validation

Before merging into the training set, run these conversations through the existing pipeline from Task 1:

```bash
python -m src.chat_checker \
    --input new_chats.jsonl \
    --output data/output/stage2_checker_report.json
```

Expected result: all 5 conversations pass structure validation and safety checks with **zero violations**, and register no near-duplicates against the original 15.

---

## ⏭️ Still Open (Not Covered in This Batch)

Stage 1 flagged additional gaps not addressed here — carried forward for a future batch:

- Persona diversity: aggressive/entitled user, elderly user, rural user, NRI/diaspora user
- Post-refusal pushback (a user who resists a redirect and insists on an answer)
- Second marriage/remarriage, fertility, and rival/enemy queries
- Fixing `conv_003`'s answer-first-data-later pattern and `conv_008`'s implicit guarantee in the *original* 15 (these are corrections to existing data, not additions)

---

*Prepared as Stage 2 of the Vedaz AI Engineer technical assessment, following the Stage 1 dataset review.*