import json
import os
from typing import Any, Dict, List, Optional, Tuple


try:
    from openai import OpenAI
except Exception:  # pragma: no cover - optional dependency at runtime
    OpenAI = None  # type: ignore


DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


class OpenAIClient:
    """Wrapper around OpenAI SDK with robust fallbacks and JSON output parsing.

    - If OPENAI_API_KEY is missing or SDK unavailable, returns mocked responses.
    - Ensures deterministic JSON output parsing with safe fallbacks.
    - Also supports Whisper transcription with graceful mock when unavailable.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, force_mock: bool = False) -> None:
        self.api_key = (api_key or os.getenv("OPENAI_API_KEY") or "").strip()
        self.model = model or DEFAULT_MODEL
        self.force_mock = force_mock
        self.is_available = bool(self.api_key and OpenAI and not self.force_mock)
        self._client = None
        if self.is_available:
            try:
                self._client = OpenAI(api_key=self.api_key)
            except Exception:
                # Fallback to mock if initialization fails
                self._client = None
                self.is_available = False

    # --------------------------- Public API --------------------------- #
    def generate_business_insights(self, prompt: str, temperature: float = 0.2) -> Dict[str, Any]:
        """Call OpenAI to generate JSON insights; return dict with keys:
        - executive_summary_en: str
        - executive_summary_hi: str
        - recommendations: List[str]
        - kpi_commentary: Dict[str, str] (optional)
        - risks: List[str] (optional)
        - opportunities: List[str] (optional)
        """
        if not self.is_available or not self._client:
            return self._mock_insights()

        try:
            response = self._client.chat.completions.create(
                model=self.model,
                temperature=temperature,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": "You are a retail analytics assistant. Always reply with compact valid JSON."},
                    {"role": "user", "content": prompt},
                ],
            )
            content = response.choices[0].message.content or "{}"
            return self._safe_json_loads(content, fallback=self._mock_insights())
        except Exception:
            return self._mock_insights()

    def transcribe_audio(self, file_bytes: bytes, filename: str = "audio.wav") -> Tuple[str, bool]:
        """Transcribe audio via Whisper if available, else mock.

        Returns (transcript, used_real_api)
        """
        if not self.is_available or not self._client:
            return (self._mock_transcript(), False)

    def availability_status(self) -> Dict[str, bool]:
        """Return flags describing what's available for this client instance."""
        return {
            "has_api_key": bool(self.api_key),
            "sdk_installed": bool(OpenAI),
            "using_mock": not self.is_available,
        }

        try:
            # The new OpenAI SDK uses the Audio namespace
            transcript = self._client.audio.transcriptions.create(
                model="whisper-1",
                file=(filename, file_bytes),
            )
            # transcript.text for SDK >=1.0
            text = getattr(transcript, "text", None) or getattr(transcript, "data", {}).get("text", "")  # type: ignore
            if not text:
                text = self._mock_transcript()
                return (text, False)
            return (text, True)
        except Exception:
            return (self._mock_transcript(), False)

    # --------------------------- Helpers --------------------------- #
    @staticmethod
    def _safe_json_loads(text: str, fallback: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        try:
            return json.loads(text)
        except Exception:
            return fallback or {}

    @staticmethod
    def _mock_insights() -> Dict[str, Any]:
        return {
            "executive_summary_en": (
                "Sales are steady with strong contribution from top SKUs. Focus on upselling "
                "high-margin items and running weekday promos to boost footfall."
            ),
            "executive_summary_hi": (
                "बिक्री स्थिर है और शीर्ष उत्पाद अच्छा योगदान दे रहे हैं। उच्च मार्जिन आइटम्स की "
                "अपसेलिंग और सप्ताह के दिनों में प्रमोशन चलाकर फुटफॉल बढ़ाएँ।"
            ),
            "recommendations": [
                "Introduce a mid-week combo offer on top 3 products to lift basket size",
                "Push low-moving inventory with 10% discount to free up cash flow",
                "Set reorder alerts for fast-moving SKUs to avoid stockouts",
            ],
            "kpi_commentary": {
                "total_revenue": "Healthy weekly trend with mild weekend spike",
                "avg_order_value": "Scope to increase via bundles and cross-sell",
            },
        }

    @staticmethod
    def _mock_transcript() -> str:
        return (
            "Today footfall was moderate. Snacks and beverages performed well. Consider a 5% weekday "
            "discount and bundle chips with soft drinks to increase average order value."
        )


