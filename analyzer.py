import json
import logging
import os
from groq import Groq
from dotenv import load_dotenv
from prompts import (
    ANALYZER_PROMPT,
    PROPOSAL_PROMPT
)
logging.basicConfig(level=logging.INFO)
load_dotenv()

MODEL = "llama-3.3-70b-versatile"

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def clean_json_response(text: str) -> str:
    return (
        text
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )


def extract_signals(job_post: str) -> dict | None:
    response = client.chat.completions.create(
        model=MODEL,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": ANALYZER_PROMPT
            },
            {
                "role": "user",
                "content": job_post
            }
        ]
    )

    raw = response.choices[0].message.content

    logging.info(f"Raw LLM response: {raw}")

    try:
        clean = clean_json_response(raw)

        data = json.loads(clean)

        required_fields = {
            "payment_verified",
            "total_spent_usd",
            "hire_rate",
            "proposal_count",
            "description_clarity",
            "external_contact_requested",
            "job_recency"
        }

        if not required_fields.issubset(data.keys()):
            logging.error("Missing required fields in response")
            return None

        return data

    except json.JSONDecodeError:
        logging.error("Invalid JSON returned from model")
        return None


def compute_score(signals: dict) -> int:
    score = 0

    if signals.get("payment_verified") is True:
        score += 20

    if signals.get("payment_verified") is False:
        score -= 20

    if (
        signals.get("total_spent_usd") is not None
        and signals["total_spent_usd"] > 10000
    ):
        score += 15

    if (
        signals.get("hire_rate") is not None
        and signals["hire_rate"] >= 70
    ):
        score += 15

    if (
        signals.get("proposal_count") is not None
        and signals["proposal_count"] < 10
    ):
        score += 10

    if (
        signals.get("proposal_count") is not None
        and signals["proposal_count"] > 50
    ):
        score -= 15

    if signals.get("description_clarity") == "high":
        score += 10

    if signals.get("description_clarity") == "low":
        score -= 10

    if signals.get("external_contact_requested") is True:
        score -= 20

    return max(0, min(score, 100))


def compute_decision(score: int) -> str:
    if score <= 39:
        return "reject"

    if score <= 69:
        return "weak"

    if score <= 84:
        return "good"

    return "strong"


def compute_confidence(signals: dict) -> float:
    total_fields = len(signals)

    available_fields = sum(
        value is not None
        for value in signals.values()
    )

    confidence = available_fields / total_fields

    return round(confidence, 2)


def analyze_job(job_post: str) -> dict:
    signals = extract_signals(job_post)

    if signals is None:
        return {
            "error": "Failed to extract signals"
        }

    score = compute_score(signals)
    decision = compute_decision(score)
    confidence = compute_confidence(signals)

    missing_fields = [
        key
        for key, value in signals.items()
        if value is None
    ]

    justification = (
        f"Score {score}/100 → {decision.upper()}. "
        f"Present signals: {len(signals) - len(missing_fields)}/{len(signals)}. "
        f"Key factors: {', '.join(k for k, v in signals.items() if v is not None)}"
    )

    return {
        "signals": signals,
        "score": score,
        "decision": decision,
        "confidence": confidence,
        "missing_fields": missing_fields,
        "justification": justification
    }


def write_proposal(
    job_post: str,
    analysis: dict
) -> str:
    context = f"""
Job Post:
{job_post}

Analysis:
Decision: {analysis["decision"]}
Score: {analysis["score"]}/100
Justification: {analysis["justification"]}
"""

    response = client.chat.completions.create(
        model=MODEL,
        temperature=0.7,
        messages=[
            {
                "role": "system",
                "content": PROPOSAL_PROMPT
            },
            {
                "role": "user",
                "content": context
            }
        ]
    )

    return response.choices[0].message.content.strip()