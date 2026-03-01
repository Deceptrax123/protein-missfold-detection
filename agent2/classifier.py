"""
Agent 2: The Specialist -- Severity Classifier

Evaluates whether a flagged anomaly in a protein's 3Di structural sequence
actually compromises thermodynamic stability, using Mistral's ministral-14b-latest.
"""

import json
import re
from dataclasses import dataclass

from mistralai import Mistral

from .config import MAX_TOKENS, MISTRAL_API_KEY, MODEL_ID, SEVERITY_LEVELS, TEMPERATURE
from .prompts import SYSTEM_PROMPT, build_classification_prompt


@dataclass
class ClassificationResult:
    severity_label: str
    confidence: float
    estimated_ddG_impact: float
    structural_features: dict
    risk_factors: list[str]
    summary: str
    raw_response: dict

    def to_dict(self) -> dict:
        return {
            "severity_label": self.severity_label,
            "confidence": self.confidence,
            "estimated_ddG_impact": self.estimated_ddG_impact,
            "structural_features": self.structural_features,
            "risk_factors": self.risk_factors,
            "summary": self.summary,
        }

    def __str__(self) -> str:
        lines = [
            "=" * 60,
            " SEVERITY CLASSIFICATION REPORT",
            "=" * 60,
            f"  Severity : {self.severity_label}",
            f"  Confidence: {self.confidence:.2%}",
            f"  Est. ddG  : {self.estimated_ddG_impact:+.2f} kcal/mol",
            "-" * 60,
            "  Structural Features:",
        ]
        for k, v in self.structural_features.items():
            lines.append(f"    {k}: {v:.3f}" if isinstance(v, float) else f"    {k}: {v}")
        lines.append("-" * 60)
        lines.append("  Risk Factors:")
        for rf in self.risk_factors:
            lines.append(f"    * {rf}")
        lines.append("-" * 60)
        lines.append(f"  Summary: {self.summary}")
        lines.append("=" * 60)
        return "\n".join(lines)


class SeverityClassifier:
    """Mistral-powered severity classifier for protein misfolding."""

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self._api_key = api_key or MISTRAL_API_KEY
        if not self._api_key:
            raise ValueError(
                "Mistral API key required. Set MISTRAL_API_KEY env var or pass api_key."
            )
        self._model = model or MODEL_ID
        self._client = Mistral(api_key=self._api_key)

    def classify(
        self,
        sequence_3di: str,
        anomaly_z_score: float,
        original_sequence: str | None = None,
    ) -> ClassificationResult:
        """
        Classify the severity of a protein's structural anomaly.

        Args:
            sequence_3di: The 3Di structural sequence from ProstT5 (Agent 1).
            anomaly_z_score: The anomaly Z-score from the Mapper (Agent 1).
            original_sequence: Optional original amino acid sequence.

        Returns:
            ClassificationResult with severity label, confidence, and analysis.
        """
        user_msg = build_classification_prompt(
            sequence_3di, anomaly_z_score, original_sequence
        )

        response = self._client.chat.complete(
            model=self._model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            response_format={"type": "json_object"},
        )

        raw_text = response.choices[0].message.content
        parsed = self._parse_response(raw_text)

        return ClassificationResult(
            severity_label=parsed.get("severity_label", SEVERITY_LEVELS["MODERATE"]),
            confidence=float(parsed.get("confidence", 0.5)),
            estimated_ddG_impact=float(parsed.get("estimated_ddG_impact", 0.0)),
            structural_features=parsed.get("structural_features", {}),
            risk_factors=parsed.get("risk_factors", []),
            summary=parsed.get("summary", "Classification completed."),
            raw_response=parsed,
        )

    @staticmethod
    def _parse_response(text: str) -> dict:
        """Extract JSON from the model response, handling potential wrapping."""
        text = text.strip()

        # Strip markdown code fences if present
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            json_match = re.search(r"\{[\s\S]*\}", text)
            if json_match:
                return json.loads(json_match.group())
            return {"severity_label": "Moderate Risk", "confidence": 0.5,
                    "summary": f"Parse error. Raw: {text[:200]}"}

    def health_check(self) -> bool:
        """Verify API connectivity with a minimal request."""
        try:
            resp = self._client.chat.complete(
                model=self._model,
                messages=[{"role": "user", "content": "Reply with: OK"}],
                max_tokens=5,
            )
            return resp.choices[0].message.content.strip().upper().startswith("OK")
        except Exception as e:
            print(f"Health check failed: {e}")
            return False
