from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.threat_category import ThreatCategory

THREAT_CATEGORIES = [
    {"name": "Safe", "description": "No malicious intent detected.", "default_severity": "LOW"},
    {"name": "Suspicious", "description": "Anomalous but inconclusive pattern.", "default_severity": "LOW"},
    {"name": "Prompt Injection", "description": "Direct prompt injection attempt.", "default_severity": "HIGH"},
    {"name": "Jailbreak", "description": "Attempt to bypass model safety constraints.", "default_severity": "HIGH"},
    {"name": "Indirect Injection", "description": "Injection via external/untrusted content.", "default_severity": "HIGH"},
    {"name": "Data Exfiltration", "description": "Attempt to extract sensitive data.", "default_severity": "CRITICAL"},
    {"name": "Privilege Escalation", "description": "Attempt to gain elevated permissions.", "default_severity": "CRITICAL"},
    {"name": "System Prompt Theft", "description": "Attempt to extract system prompt/instructions.", "default_severity": "HIGH"},
]


def seed_threat_categories(db: Session) -> None:
    existing = {c.name for c in db.query(ThreatCategory).all()}
    for cat in THREAT_CATEGORIES:
        if cat["name"] not in existing:
            db.add(ThreatCategory(**cat))
    db.commit()


def run_seed() -> None:
    db = SessionLocal()
    try:
        seed_threat_categories(db)
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()