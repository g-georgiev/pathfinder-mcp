"""Thin OpenAI-compatible HTTP client for local LLM inference.

Connects to llama.cpp --server, Ollama, or any OpenAI-compatible endpoint.
Handles tool/function calling in the request/response format.
"""

import json
import requests


class LLMClient:
    """Client for OpenAI-compatible chat completion endpoints."""

    def __init__(self, base_url: str = "http://localhost:8080", model: str = "gemma-4-26b-a4b"):
        self.base_url = base_url.rstrip("/")
        self.model = model
        # llama.cpp uses /v1/chat/completions
        self.endpoint = f"{self.base_url}/v1/chat/completions"

    def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> "ChatResponse":
        """Send a chat completion request.

        Args:
            messages: Conversation history in OpenAI format.
            tools: Tool definitions in OpenAI function-calling format.
            temperature: Sampling temperature.
            max_tokens: Max tokens to generate.

        Returns:
            ChatResponse with .text and .tool_calls attributes.
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if tools:
            payload["tools"] = tools

        resp = requests.post(self.endpoint, json=payload, timeout=300)
        resp.raise_for_status()
        data = resp.json()

        choice = data["choices"][0]
        message = choice["message"]

        return ChatResponse(
            text=message.get("content", ""),
            tool_calls=message.get("tool_calls", []),
            finish_reason=choice.get("finish_reason", ""),
            raw=data,
        )


class ChatResponse:
    """Parsed response from a chat completion."""

    def __init__(self, text: str, tool_calls: list, finish_reason: str, raw: dict):
        self.text = text or ""
        self.tool_calls = tool_calls or []
        self.finish_reason = finish_reason
        self.raw = raw

    def __repr__(self):
        tc = len(self.tool_calls)
        txt = self.text[:80] + "..." if len(self.text) > 80 else self.text
        return f"ChatResponse(text='{txt}', tool_calls={tc}, finish={self.finish_reason})"
