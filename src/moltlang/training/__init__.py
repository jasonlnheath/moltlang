"""
MoltLang Training Module.

This module provides functionality for training models on MoltLang.
"""

__version__ = "0.1.0"

from moltlang.training.data_gen import SyntheticDataGenerator
from moltlang.training.distill import KnowledgeDistillation

__all__ = ["SyntheticDataGenerator", "KnowledgeDistillation"]
