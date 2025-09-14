import json
import os
from typing import Any, Dict, List, Optional, Tuple


try:
    import google.generativeai as genai
except Exception:  # pragma: no cover - optional dependency at runtime
    genai = None  # type: ignore


DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")


class GeminiClient:
    """Wrapper around Google Gemini SDK with robust fallbacks and JSON output parsing.

    - If GEMINI_API_KEY is missing or SDK unavailable, returns mocked responses.
    - Ensures deterministic JSON output parsing with safe fallbacks.
    - Provides similar interface to OpenAIClient for easy switching.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, force_mock: bool = False) -> None:
        self.api_key = (api_key or os.getenv("GEMINI_API_KEY") or "").strip()
        self.model = model or DEFAULT_MODEL
        self.force_mock = force_mock
        self.is_available = bool(self.api_key and genai and not self.force_mock)
        self._client = None
        
        if self.is_available:
            try:
                genai.configure(api_key=self.api_key)
                self._client = genai.GenerativeModel(self.model)
            except Exception:
                # Fallback to mock if initialization fails
                self._client = None
                self.is_available = False

    # --------------------------- Public API --------------------------- #
    def generate_business_insights(self, prompt: str, temperature: float = 0.2) -> Dict[str, Any]:
        """Call Gemini to generate JSON insights; return dict with keys:
        - executive_summary_en: str
        - executive_summary_hi: str
        - recommendations: List[str]
        - recommendations_hi: List[str]
        - kpi_commentary: Dict[str, str] (optional)
        - kpi_commentary_hi: Dict[str, str] (optional)
        - risks: List[str] (optional)
        - opportunities: List[str] (optional)
        """
        if not self.is_available or not self._client:
            raise RuntimeError("Gemini API is not available. Please check your API key and internet connection.")

        try:
            # Configure generation parameters
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                top_p=0.8,
                top_k=40,
                max_output_tokens=2048,
                response_mime_type="application/json"
            )
            
            response = self._client.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            content = response.text or "{}"
            result = self._safe_json_loads(content, fallback={})
            
            if not result:
                raise RuntimeError("Failed to generate valid insights from Gemini API.")
            
            return result
        except Exception as e:
            raise RuntimeError(f"Gemini API error: {str(e)}")

    def transcribe_audio(self, file_bytes: bytes, filename: str = "audio.wav") -> Tuple[str, bool]:
        """Transcribe audio via Gemini if available, else mock.

        Returns (transcript, used_real_api)
        """
        if not self.is_available or not self._client:
            return (self._mock_transcript(), False)

        try:
            # For Gemini, we need to convert audio to text first
            # This is a simplified implementation - in practice, you might need
            # to use a different approach for audio transcription with Gemini
            import base64
            
            # Convert audio bytes to base64
            audio_base64 = base64.b64encode(file_bytes).decode('utf-8')
            
            # Create a prompt for audio transcription
            audio_prompt = f"""
            Please transcribe the following audio file ({filename}) and provide a business summary.
            Focus on retail/shop insights, sales data, customer feedback, or operational observations.
            Keep the response concise and business-focused.
            """
            
            # Note: This is a simplified approach. For production, you might want to use
            # a dedicated audio transcription service or Google Cloud Speech-to-Text
            response = self._client.generate_content(audio_prompt)
            transcript = response.text or self._mock_transcript()
            
            return (transcript, True)
        except Exception:
            return (self._mock_transcript(), False)

    def availability_status(self) -> Dict[str, bool]:
        """Return flags describing what's available for this client instance."""
        return {
            "has_api_key": bool(self.api_key),
            "sdk_installed": bool(genai),
            "using_mock": not self.is_available,
        }

    # --------------------------- Helpers --------------------------- #
    @staticmethod
    def _safe_json_loads(text: str, fallback: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        try:
            return json.loads(text)
        except Exception:
            return fallback or {}

