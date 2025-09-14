"""
AI Client Factory - Provides a unified interface for different AI providers.
Supports OpenAI and Google Gemini with automatic fallback and provider selection.
"""

import os
from typing import Any, Dict, List, Optional, Tuple, Union
from enum import Enum


class AIProvider(Enum):
    """Supported AI providers."""
    OPENAI = "openai"
    GEMINI = "gemini"
    AUTO = "auto"  # Automatically choose based on available API keys


class AIClient:
    """
    Unified AI client that can work with different providers.
    Automatically selects the best available provider or allows manual selection.
    """

    def __init__(
        self, 
        provider: Union[AIProvider, str] = AIProvider.GEMINI,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        force_mock: bool = False
    ):
        self.provider = AIProvider(provider) if isinstance(provider, str) else provider
        self.api_key = api_key
        self.model = model
        self.force_mock = force_mock
        self._client = None
        self._provider_name = None
        
        self._initialize_client()

    def _initialize_client(self):
        """Initialize the appropriate AI client based on provider selection."""
        if self.provider == AIProvider.AUTO:
            self._client, self._provider_name = self._auto_select_provider()
        elif self.provider == AIProvider.OPENAI:
            self._client, self._provider_name = self._init_openai()
        elif self.provider == AIProvider.GEMINI:
            self._client, self._provider_name = self._init_gemini()
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def _auto_select_provider(self) -> Tuple[Any, str]:
        """Automatically select the best available provider based on API keys."""
        # Check for Gemini API key first (preferred)
        gemini_key = self.api_key or os.getenv("GEMINI_API_KEY")
        if gemini_key and not self.force_mock:
            try:
                from .gemini_client import GeminiClient
                client = GeminiClient(api_key=gemini_key, model=self.model, force_mock=self.force_mock)
                if client.is_available:
                    return client, "Gemini"
            except Exception:
                pass

        # Check for OpenAI API key as fallback
        openai_key = self.api_key or os.getenv("OPENAI_API_KEY")
        if openai_key and not self.force_mock:
            try:
                from .openai_client import OpenAIClient
                client = OpenAIClient(api_key=openai_key, model=self.model, force_mock=self.force_mock)
                if client.is_available:
                    return client, "OpenAI"
            except Exception:
                pass

        # If no API keys available, raise error
        raise RuntimeError("No AI API keys found. Please add GEMINI_API_KEY or OPENAI_API_KEY to your .env file.")

    def _init_openai(self) -> Tuple[Any, str]:
        """Initialize OpenAI client."""
        from .openai_client import OpenAIClient
        client = OpenAIClient(api_key=self.api_key, model=self.model, force_mock=self.force_mock)
        return client, "OpenAI"

    def _init_gemini(self) -> Tuple[Any, str]:
        """Initialize Gemini client."""
        from .gemini_client import GeminiClient
        client = GeminiClient(api_key=self.api_key, model=self.model, force_mock=self.force_mock)
        return client, "Gemini"

    # --------------------------- Public API --------------------------- #
    def generate_business_insights(self, prompt: str, temperature: float = 0.2) -> Dict[str, Any]:
        """Generate business insights using the configured provider."""
        return self._client.generate_business_insights(prompt, temperature)

    def transcribe_audio(self, file_bytes: bytes, filename: str = "audio.wav") -> Tuple[str, bool]:
        """Transcribe audio using the configured provider."""
        return self._client.transcribe_audio(file_bytes, filename)

    def availability_status(self) -> Dict[str, Any]:
        """Get availability status for the current provider."""
        status = self._client.availability_status()
        status["provider"] = self._provider_name
        status["provider_type"] = self.provider.value
        return status

    def get_provider_info(self) -> Dict[str, str]:
        """Get information about the current provider."""
        return {
            "provider": self._provider_name,
            "provider_type": self.provider.value,
            "model": getattr(self._client, 'model', 'unknown'),
            "is_available": self._client.is_available if hasattr(self._client, 'is_available') else False
        }

    @classmethod
    def get_available_providers(cls) -> List[Dict[str, Any]]:
        """Get list of available providers and their status."""
        providers = []
        
        # Check OpenAI
        try:
            from .openai_client import OpenAIClient
            openai_client = OpenAIClient()
            providers.append({
                "name": "OpenAI",
                "type": AIProvider.OPENAI.value,
                "available": openai_client.is_available,
                "status": openai_client.availability_status()
            })
        except Exception:
            providers.append({
                "name": "OpenAI",
                "type": AIProvider.OPENAI.value,
                "available": False,
                "status": {"error": "Import failed"}
            })

        # Check Gemini
        try:
            from .gemini_client import GeminiClient
            gemini_client = GeminiClient()
            providers.append({
                "name": "Gemini",
                "type": AIProvider.GEMINI.value,
                "available": gemini_client.is_available,
                "status": gemini_client.availability_status()
            })
        except Exception:
            providers.append({
                "name": "Gemini",
                "type": AIProvider.GEMINI.value,
                "available": False,
                "status": {"error": "Import failed"}
            })

        return providers
