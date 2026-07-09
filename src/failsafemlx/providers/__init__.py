"""Optional LLM provider abstraction for FailSafeML-X.

Default provider is deterministic local fallback. External providers are opt-in only.
"""

from failsafemlx.providers.router import get_provider, generate_reliability_explanation

__all__ = ["get_provider", "generate_reliability_explanation"]
