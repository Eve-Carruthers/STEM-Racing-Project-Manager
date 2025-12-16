"""
Risk management models and helpers.

This module defines a ``Risk`` dataclass and helper functions for
categorising and analysing risks.  In a full web application these
structures could be stored in a database and visualised in dashboards.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Risk:
    """Represents a risk with probability and impact ratings.

    Probabilities and impacts are scored on a 1–5 scale where 1 is low
    and 5 is high.  The product of probability and impact yields an
    overall risk score.
    """

    name: str
    description: str
    probability: int  # 1–5
    impact: int  # 1–5
    owner: Optional[str] = None
    mitigation: Optional[str] = None

    @property
    def score(self) -> int:
        return self.probability * self.impact

    def severity(self) -> str:
        """Return a qualitative category based on the risk score."""
        score = self.score
        if score >= 16:
            return "High"
        elif score >= 9:
            return "Medium"
        else:
            return "Low"

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.name} (score {self.score}, {self.severity()})"