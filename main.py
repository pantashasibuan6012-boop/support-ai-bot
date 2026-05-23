#!/usr/bin/env python3
"""Support AI Bot - Customer support automation."""

import json, sys
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class Sentiment(Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    ANGRY = "angry"

@dataclass
class Ticket:
    id: int
    text: str
    channel: str = "web"
    priority: Priority = Priority.MEDIUM
    sentiment: Sentiment = Sentiment.NEUTRAL
    category: str = ""
    auto_response: str = ""
    confidence: float = 0.0

class SupportBot:
    CATEGORIES = {
        "billing": ["invoice", "payment", "charge", "refund", "subscription"],
        "shipping": ["delivery", "shipping", "track", "arrived", "lost"],
        "technical": ["error", "bug", "crash", "not working", "broken"],
        "account": ["login", "password", "account", "access", "locked"],
        "general": ["question", "help", "info", "how"],
    }

    def __init__(self):
        self.tickets = []
        self.responses = {
            "billing": "Thank you for reaching out about billing. Our team will review your account and respond within 24 hours.",
            "shipping": "We understand shipping concerns are frustrating. Let me check your order status right away.",
            "technical": "Sorry for the technical issue. Could you provide more details about the error you're seeing?",
            "account": "For account security, we'll verify your identity and help you regain access shortly.",
            "general": "Thank you for contacting us! We'll get back to you as soon as possible.",
        }

    def classify(self, text: str) -> Ticket:
        ticket = Ticket(id=len(self.tickets) + 1, text=text)
        lower = text.lower()

        # Classify category
        scores = {}
        for cat, keywords in self.CATEGORIES.items():
            scores[cat] = sum(1 for kw in keywords if kw in lower)
        ticket.category = max(scores, key=scores.get) if max(scores.values()) > 0 else "general"

        # Determine priority
        urgent_words = ["urgent", "asap", "immediately", "critical", "emergency"]
        if any(w in lower for w in urgent_words):
            ticket.priority = Priority.CRITICAL
        elif any(w in lower for w in ["refund", "cancel", "broken"]):
            ticket.priority = Priority.HIGH

        # Sentiment
        neg_words = ["angry", "terrible", "worst", "horrible", "unacceptable"]
        pos_words = ["thank", "great", "love", "excellent", "happy"]
        neg = sum(1 for w in neg_words if w in lower)
        pos = sum(1 for w in pos_words if w in lower)
        if neg >= 2:
            ticket.sentiment = Sentiment.ANGRY
        elif neg > pos:
            ticket.sentiment = Sentiment.NEGATIVE
        elif pos > neg:
            ticket.sentiment = Sentiment.POSITIVE

        ticket.auto_response = self.responses.get(ticket.category, self.responses["general"])
        ticket.confidence = min(0.95, 0.6 + scores.get(ticket.category, 0) * 0.1)
        self.tickets.append(ticket)
        return ticket

    def stats(self) -> dict:
        cats = {}
        for t in self.tickets:
            cats[t.category] = cats.get(t.category, 0) + 1
        return {"total": len(self.tickets), "by_category": cats}

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py classify 'ticket text'")
        sys.exit(1)
    if sys.argv[1] == "classify":
        text = " ".join(sys.argv[2:])
        bot = SupportBot()
        ticket = bot.classify(text)
        print(json.dumps({
            "id": ticket.id, "category": ticket.category,
            "priority": ticket.priority.name, "sentiment": ticket.sentiment.value,
            "confidence": ticket.confidence, "response": ticket.auto_response,
        }, indent=2))

if __name__ == "__main__":
    main()
