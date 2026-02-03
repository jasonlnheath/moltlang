"""
Synthetic data generation for MoltLang training.

This module generates synthetic training data for fine-tuning models
on MoltLang.
"""

import random
from typing import Any

from moltlang import translate_to_molt
from moltlang.tokens import TokenType


class SyntheticDataGenerator:
    """
    Generate synthetic training data for MoltLang.

    Creates pairs of human language text and MoltLang translations
    for training and fine-tuning language models.
    """

    def __init__(self):
        """Initialize the data generator."""
        self.templates = self._load_templates()

    def _load_templates(self) -> list[dict[str, Any]]:
        """Load templates for data generation."""
        return [
            {
                "pattern": "Fetch {data} from {source}",
                "tokens": ["OP:FETCH", "SRC:{source}"],
                "values": {
                    "data": ["data", "user", "records", "information"],
                    "source": ["API", "database", "file", "cache"],
                },
            },
            {
                "pattern": "Parse {data_type} from {source}",
                "tokens": ["OP:PARSE", "SRC:{source}"],
                "values": {
                    "data_type": ["JSON", "XML", "CSV", "text"],
                    "source": ["file", "API", "stream", "buffer"],
                },
            },
            {
                "pattern": "Search for {query} in {source}",
                "tokens": ["OP:SEARCH", "SRC:{source}"],
                "values": {
                    "query": ["user", "record", "data", "item"],
                    "source": ["database", "file", "memory", "cache"],
                },
            },
            {
                "pattern": "Transform {data} and return {format}",
                "tokens": ["OP:TRANSFORM", "RET:{format}"],
                "values": {
                    "data": ["data", "input", "content"],
                    "format": ["JSON", "text", "list", "dict"],
                },
            },
            {
                "pattern": "Validate {input} from {source}",
                "tokens": ["OP:VALIDATE", "SRC:{source}"],
                "values": {
                    "input": ["input", "data", "parameters", "request"],
                    "source": ["API", "form", "file", "stream"],
                },
            },
        ]

    def generate(self, count: int = 100) -> list[dict[str, str]]:
        """
        Generate synthetic training examples.

        Args:
            count: Number of examples to generate

        Returns:
            List of training examples with 'input' and 'output' keys
        """
        examples = []

        for _ in range(count):
            template = random.choice(self.templates)
            example = self._generate_from_template(template)
            examples.append(example)

        return examples

    def _generate_from_template(self, template: dict[str, Any]) -> dict[str, str]:
        """Generate a single example from a template."""
        pattern = template["pattern"]
        values = template["values"]

        # Fill in random values
        text = pattern
        for key, options in values.items():
            text = text.replace(f"{{{key}}}", random.choice(options))

        # Generate MoltLang translation
        molt = translate_to_molt(text)

        return {"input": text, "output": molt.text}

    def save_to_file(self, examples: list[dict[str, str]], filepath: str) -> None:
        """
        Save examples to a JSONL file.

        Args:
            examples: List of training examples
            filepath: Path to save the file
        """
        import json

        with open(filepath, "w") as f:
            for example in examples:
                f.write(json.dumps(example) + "\n")
