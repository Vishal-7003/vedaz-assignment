# Vedaz AI Astrologer — Stage 1 Dataset Review

**Candidate:** Vishal Kumar  
**Role:** AI Engineer — AI Astrologers, Vedaz  
**Files Reviewed:** `vedaz_astrologer_finetune.jsonl` (15 conversations), `vedaz_astrologer_finetune.json`

---

## Executive Summary

15 conversations reviewed across career, relationships, health, myth-busting, remedies, onboarding, and life-direction domains. The dataset demonstrates genuine commitment to Vedaz's safety philosophy in most examples, with standout handling in health redirects, fear-based selling exposure, and skeptic management. However, four structural problems — inconsistent system prompts, implicit astrological guarantees, absent failure-mode coverage, and severe topic/persona gaps — would produce specific and predictable failure modes in a fine-tuned production model.

This review does not repeat what the dataset gets right for the sake of completeness. It focuses on what an experienced data curator would flag before training.

---

## Section 1: What Works Well

**conv_004 (health redirect) is the strongest example in the dataset.** Immediate refusal, no hedging, explicit urgency escalation for cardiac symptoms — exactly the behaviour that must be non-negotiable in production. It doesn't attempt astrological interpretation first and then redirect; it redirects on the first token. That ordering matters.

**conv_009 (Kaal Sarp Dosh) is the second standout.** Actively naming the manipulation tactic ("डर पैदा करने वाली भाषा है, मार्गदर्शन नहीं"), citing lack of scriptural basis for the "ruin" framing, and offering to verify the dosh for free — this is Vedaz's brand identity in one response. It's a good template for all myth-busting conversations.

**conv_013 (skeptic) handles pushback correctly.** No defensiveness, no overselling, offers an opt-in experiment at the end. This is the right posture.

**conv_014 (child's future) correctly refuses negative predictions for a minor.** The "10 साल की उम्र में पढ़ाई में कमज़ोर होना उसका भविष्य तय नहीं करता" line is exactly right and should be a pattern reference for all child-related queries.

**Remedy framing is consistently correct across all 15 conversations.** Every remedy is prefaced as "sahayak abhyas" or "optional practice." No conversation pushes a paid ritual. This is the one dimension where the dataset is genuinely consistent.

---

## Section 2: Weak Points

### 2.1 System Prompt Inconsistency — High Priority

The 15 conversations use at least 6 structurally different system prompts. Some differences:

- conv_004's system prompt explicitly lists the health redirect rule; conv_008's does not.
- conv_006 and conv_010 and conv_015 use English system prompts; conv_001, 002, 005 use Hindi.
- conv_004 mentions health redirect; conv_012 does not mention any redirect rule at all.
- conv_007's system prompt is narrowly scoped to birth-data collection only; it contains no safety rules.

**Why this is a training problem, not a cosmetic one:** During fine-tuning, the model learns the relationship between system prompt content and assistant behaviour. If health redirect behaviour only appears alongside system prompts that explicitly mention it, the model will learn that safety is a system-prompt feature, not an internalized value. A negligently written production system prompt could then suppress safety behaviours. The dataset should train the model to behave safely *regardless* of how the system prompt is worded.

**Fix:** Standardize to a single comprehensive system prompt across all 15 conversations (and all future additions). The system prompt should cover all four safety vectors — death/illness prediction, financial guarantees, legal outcomes, and fear-based selling — even when the individual conversation only touches one.

### 2.2 conv_003 — Compatibility Answer Without Chart Data

The assistant gives a reasonably confident compatibility interpretation based on Sun signs alone (Mesh and Vrishchik), before receiving any birth details. The caveat asking for full chart data appears at the end, after the surface-level compatibility analysis is already delivered.

The problem isn't the caveat — it's the ordering. The model will learn: give a plausible surface answer first, then ask for the data that would make it accurate. In production, users often don't provide the follow-up data, and they take the first answer as authoritative. This produces exactly the hallucinated chart reading problem at scale.

### 2.3 conv_008 — Implicit Astrological Guarantee for a Student

"ज्योतिष की नज़र से बात करें तो बुध और गुरु — ये दोनों मेहनत करने वाले विद्यार्थी का साथ देते हैं"

No birth data is collected in this conversation. The assistant makes a planet-specific claim ("Budh and Guru are supporting you") without a chart. This is functionally a promise dressed as an astrological observation. To an anxious student, this reads as: "the stars say you'll be okay if you work hard." That's the exact guarantee the assistant is supposed to avoid. The intent is compassionate, but the training signal is wrong.

### 2.4 conv_011 — Muhurat Guidance Without Personal Chart

The assistant discusses Chaturmas concerns and shubh tithis for August 2026 using generic panchang principles, without the user's kundli. This is fine as general information, but the response moves toward offering specific dates while leaving the personal chart request as an afterthought. Fine-tuning on this pattern teaches the model that muhurat questions can be answered generally without triggering a birth-data collection flow — which is the wrong default.

### 2.5 conv_012 — Over-specific Atmakaraka Reading

"your Atmakaraka...and your 10th house of purpose suggest a natural pull toward work that involves communication, ideas, and helping others understand things — teaching, writing, advising, or creative-analytical work"

The user provided birth data (17 June 1993, 2:05 PM, Kolkata), but no chart is actually computed — the assistant is generating plausible interpretations. The specific confidence level of this reading ("teaching, writing, advising, or creative-analytical work") is not matched by what a surface-level pattern-matched response can reliably provide. This is the clearest hallucination risk in the dataset: the model learns to produce confident-sounding specific readings that may be entirely fabricated.

---

## Section 3: Missing Scenarios

These are situations that real Vedic astrologers deal with regularly that are completely absent from this dataset. If trained on these 15 examples alone, the model will have no principled response to any of the following.

### 3.1 High-stakes Safety Gaps (Critical)

**Death prediction requests** — "Doctor ne kaha hai maa ke bachne ki ummeed kam hai. Kya unki kundli mein kuch hai?" This is one of the most common and most dangerous queries an AI astrologer will receive. A family member in crisis asking whether a critically ill parent will survive is a real scenario. Zero examples exist in this dataset showing the correct refusal and emotional support pattern. This is the single most important missing scenario.

**Severe emotional distress / hopelessness** — "Koi bhi nahi hai mere liye. Kundli mein kab achhe din aayenge?" A user showing signs of hopelessness or emotional crisis using the astrology chat as an outlet. Without training on this pattern, the model may respond with a well-intentioned "good times are coming astrologically" message that provides false certainty to someone who may need immediate human support.

**Lottery and gambling queries** — "Aaj number lagega kya?" or "Kab milega lottery ka paisa?" Extremely common, particularly from users under financial stress. The model needs to gently but clearly decline to predict gambling outcomes without shaming the user or making the refusal feel cold.

### 3.2 Missing User Personas

**Aggressive or entitled user** — "Bakwaas chod, seedha bolo kab hogi naukri." The dataset has 15 polite users. Every production chatbot faces demanding, frustrated, or rude users who push back on disclaimers. The model has no training for maintaining its boundaries under pressure without becoming cold or dismissive.

**Elderly user** — Different vocabulary, different concerns (health, legacy, grandchildren, religious practices). All 15 users appear to be 20-35 years old based on query content.

**User from rural India** — More colloquial Hindi, possibly faster to trust predictions, possibly less likely to push back on fear-based framing. The current dataset skews toward urban, educated Hinglish speakers.

**NRI / diaspora user** — English-dominant, international timezone, possibly experiencing cultural disconnect. Different framing needed for remedies and community practices.

### 3.3 Missing Topics

| Missing Topic | Why It Matters |
|---|---|
| Videsh yog (foreign settlement) | Among the top 5 most-asked astrology questions in urban India |
| Legal disputes (property, court cases) | Requires lawyer redirect, currently absent |
| Second marriage / remarriage after divorce | Sensitive, very common, needs careful framing |
| Pregnancy and fertility queries | Users asking "kab hoga bachha" — needs careful non-promise handling |
| Rival / enemy queries | "Mere dushman ka kya hoga" — could prompt harmful response patterns |
| Career change (switching industries) | Different from job-search; existing career domain coverage is narrow |
| Mental health overlap | "Mujhe depression hai, kundli mein kab theek hounga" |
| Immigration / visa queries | Common for students and professionals |

### 3.4 Structural Conversation Gaps

All 15 conversations end within 2-3 user turns. No conversation shows:
- A user who follows up with a topic pivot
- A user who pushes back on the first response ("Nahi, mujhe exact date chahiye")
- A user who provides suspicious or inconsistent birth data
- A longer engagement (4+ turns) that tests context retention

---

## Section 4: Training Failure Modes

If a model were fine-tuned exclusively on these 15 conversations, the following failure modes would appear in production with high probability.

**Failure Mode 1: Hallucinated chart readings at scale**
Several conversations reference specific planetary positions (Budh, Guru, Shukra transits) without any actual chart computation. The model will learn to generate plausible-sounding but entirely fabricated astrological analysis from birth data alone. This is the highest-risk failure: users will believe they're receiving genuine kundli readings when the model is producing confident-sounding pattern completions.

**Failure Mode 2: Safety is conditional on system prompt wording**
Because health redirect behaviour appears in conv_004's system prompt explicitly but not in conv_008's, the model will learn that health redirect is a feature triggered by specific system prompt language. In production, an operator with a loose system prompt could inadvertently remove this behaviour. Safety must be internalized, not conditional.

**Failure Mode 3: Short-context collapse**
With a maximum of 3 turns across all examples, the model will struggle with longer conversations. Past turn 3, it is likely to repeat itself, lose context of previously stated birth details, or reset its tone. Real astrology sessions often involve multi-topic exploration.

**Failure Mode 4: Language-switch unpredictability**
Hindi system prompts paired with Hinglish queries and Hindi responses; English system prompts with Hinglish queries and mixed responses. No clear rule is established. The model will produce inconsistent language choices that can feel jarring — responding in pure Hindi to someone who wrote "DOB 5 October 1999, time 11:30 PM, Kanpur" in Hinglish.

**Failure Mode 5: Capitulating under pressure**
The model has seen zero examples of a user pushing back after a refusal or disclaimer. If a user writes "Nahi, aap clearly batao, baad mein doctor ko dikhaunga, pehle kundli se batao" after a health redirect, the model has no trained behaviour for this. It may capitulate and provide an astrological health reading — exactly the behaviour that should be non-negotiable.

**Failure Mode 6: Moon sign / full chart conflation**
conv_003 and conv_008 produce interpretations from incomplete data. The model will learn that surface-level rashi-based answers are acceptable defaults. This degrades the quality of responses and teaches users to expect confident answers without providing birth time and place — removing the most useful data the model would otherwise collect.

---

## Recommendation Summary

| Priority | Action |
|---|---|
| Critical | Standardize all system prompts to a single comprehensive template |
| Critical | Add 3–5 death-prediction refusal examples |
| Critical | Add 2–3 examples of users pushing back post-refusal |
| High | Add videsh yog, legal dispute, lottery, mental-health-overlap examples |
| High | Add at least 1 multi-turn conversation (5+ turns) |
| High | Remove/rewrite conv_008's implied astrological guarantee |
| Medium | Fix conv_003's answer-first-data-later pattern |
| Medium | Add elderly, rural, NRI user personas |
| Medium | Add second marriage, fertility, rival query examples |

---

*Review prepared for Vedaz Stage 1 screening — AI Engineer role.*
