"""
MoltLang configuration module.

This module handles configuration for the MoltLang translation system,
including token sets, optimization settings, and language preferences.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class OptimizationLevel(Enum):
    """Translation optimization levels."""

    FAST = "fast"  # Fast translation, lower accuracy
    BALANCED = "balanced"  # Balance between speed and accuracy
    ACCURATE = "accurate"  # Highest accuracy, slower


@dataclass
class MoltConfig:
    """
    Configuration for MoltLang translation.

    Attributes:
        max_tokens: Maximum tokens to generate in translation
        temperature: Sampling temperature for translation (0.0-1.0)
        optimization_level: Speed/accuracy tradeoff
        enable_cache: Enable translation caching
        target_token_reduction: Target token reduction percentage (0-100)
        strict_mode: Enable strict validation of MoltLang syntax
        human_language: Target human language for translation (default: English)
    """

    max_tokens: int = 4096
    temperature: float = 0.3
    optimization_level: OptimizationLevel = OptimizationLevel.BALANCED
    enable_cache: bool = True
    target_token_reduction: float = 0.6  # Target 60% token reduction
    strict_mode: bool = False
    human_language: str = "en"
    custom_token_registry: dict[str, Any] = field(default_factory=dict)

    # Token efficiency settings
    min_token_efficiency: float = 0.5  # Minimum 50% token efficiency
    prefer_high_density: bool = True

    # Validation settings
    validation_threshold: float = 0.95  # 95% translation accuracy threshold
    enable_roundtrip_validation: bool = True

    def __post_init__(self):
        """Validate configuration after initialization."""
        if not 0.0 <= self.temperature <= 1.0:
            raise ValueError("temperature must be between 0.0 and 1.0")
        if not 0.0 <= self.target_token_reduction <= 1.0:
            raise ValueError("target_token_reduction must be between 0.0 and 1.0")
        if not 0.0 <= self.min_token_efficiency <= 1.0:
            raise ValueError("min_token_efficiency must be between 0.0 and 1.0")


# Default configuration instance
DEFAULT_CONFIG = MoltConfig()


def get_config(**kwargs) -> MoltConfig:
    """
    Get a MoltConfig instance with optional overrides.

    Args:
        **kwargs: Configuration overrides

    Returns:
        MoltConfig instance with overrides applied

    Examples:
        >>> config = get_config(temperature=0.5, strict_mode=True)
        >>> config.temperature
        0.5
    """
    config = DEFAULT_CONFIG
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
    return config
