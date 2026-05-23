"""
session.py — Manages conversation state across all 4 stages.
"""

import json
from datetime import datetime


class Session:
    STAGES = ["faq", "qualify", "summary"]

    def __init__(self):
        self.stage = "faq"
        self.history = []
        self.lead_data = {}
        self.escalated = False
        self.escalation_log = []
        self.sop_gaps = []
        self.unanswered_count = 0
        self.qualify_question_index = 0
        self.session_start = datetime.now().isoformat()
        self.summary = None

    def add_message(self, role: str, content: str):
        self.history.append({"role": role, "content": content})

    def log_escalation(self, trigger: str, customer_message: str, reason: str):
        event = {
            "timestamp": datetime.now().isoformat(),
            "trigger": trigger,
            "reason": reason,
            "customer_message": customer_message,
            "stage": self.stage
        }
        self.escalation_log.append(event)
        self.escalated = True

    def log_sop_gap(self, question: str):
        self.sop_gaps.append(question)
        self.unanswered_count += 1

    def advance_stage(self):
        current_index = self.STAGES.index(self.stage)
        if current_index < len(self.STAGES) - 1:
            self.stage = self.STAGES[current_index + 1]

    def to_dict(self) -> dict:
        return {
            "session_start": self.session_start,
            "session_end": datetime.now().isoformat(),
            "stage_at_end": self.stage,
            "escalated": self.escalated,
            "escalation_log": self.escalation_log,
            "lead_data": self.lead_data,
            "sop_gaps": self.sop_gaps,
            "unanswered_count": self.unanswered_count,
            "turn_count": len([m for m in self.history if m["role"] == "user"]),
            "summary": self.summary,
            "conversation_history": self.history
        }

    def save_log(self, log_dir: str = "logs"):
        import os
        os.makedirs(log_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(log_dir, f"session_{timestamp}.json")
        try:
            with open(filepath, "w") as f:
                json.dump(self.to_dict(), f, indent=2)
            return filepath
        except Exception as e:
            print(f"[WARNING] Could not save session log: {e}")
            return None
