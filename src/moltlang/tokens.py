"""
MoltLang token system.

This module defines the token types, token registry, and token operations
for the MoltLang language system.

LLM-Friendly Design: All token values use lowercase for natural generation.
The parser is case-insensitive and accepts both [RET:json] and [RET:JSON].
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class TokenType(Enum):
    """
    Types of tokens in the MoltLang language.

    Low-hanging fruit categories for MVP:
    - Operations: Common AI actions (fetch, parse, transform, etc.)
    - Sources: Data sources (API, database, file, etc.)
    - Parameters: Common parameter types
    - Returns: Return value types
    - Control: Control flow structures

    Note: All values are lowercase for LLM-friendliness.
    The parser accepts both cases (case-insensitive).
    """

    # Operation tokens - core AI actions
    OP_FETCH = "OP:fetch"  # Retrieve data
    OP_PARSE = "OP:parse"  # Parse structured data
    OP_TRANSFORM = "OP:transform"  # Transform data
    OP_VALIDATE = "OP:validate"  # Validate input
    OP_COMPUTE = "OP:compute"  # Perform computation
    OP_SEARCH = "OP:search"  # Search for data
    OP_FILTER = "OP:filter"  # Filter data
    OP_MAP = "OP:map"  # Map over data
    OP_REDUCE = "OP:reduce"  # Reduce data
    OP_AGGREGATE = "OP:aggregate"  # Aggregate results
    OP_PROCESS = "OP:process"  # Process data

    # Source tokens - data sources
    SRC_API = "SRC:api"  # REST/GraphQL API
    SRC_DB = "SRC:db"  # Database
    SRC_FILE = "SRC:file"  # File system
    SRC_MEM = "SRC:mem"  # In-memory data
    SRC_STREAM = "SRC:stream"  # Data stream
    SRC_QUEUE = "SRC:queue"  # Message queue
    SRC_CACHE = "SRC:cache"  # Cache layer

    # Parameter tokens - common parameter types
    PARAM_TOKEN = "PARAM:token"  # Authentication token
    PARAM_KEY = "PARAM:key"  # API key or identifier
    PARAM_QUERY = "PARAM:query"  # Query string
    PARAM_BODY = "PARAM:body"  # Request body
    PARAM_HEADER = "PARAM:header"  # HTTP header
    PARAM_TIMEOUT = "PARAM:timeout"  # Timeout value
    PARAM_LIMIT = "PARAM:limit"  # Result limit
    PARAM_OFFSET = "PARAM:offset"  # Pagination offset
    PARAM_TIMES = "PARAM:times"  # Retry count / repetition count

    # Return type tokens
    RET_JSON = "RET:json"  # JSON format
    RET_TEXT = "RET:text"  # Plain text
    RET_BIN = "RET:bin"  # Binary data
    RET_STREAM = "RET:stream"  # Streaming response
    RET_BOOL = "RET:bool"  # Boolean result
    RET_NUM = "RET:num"  # Numeric result
    RET_LIST = "RET:list"  # List result
    RET_DICT = "RET:dict"  # Dictionary result
    RET_NULL = "RET:null"  # Null/void result

    # Control flow tokens
    CTL_IF = "CTL:if"  # Conditional
    CTL_ELSE = "CTL:else"  # Alternative
    CTL_LOOP = "CTL:loop"  # Loop/iterate
    CTL_BREAK = "CTL:break"  # Exit loop
    CTL_CONTINUE = "CTL:continue"  # Next iteration
    CTL_TRY = "CTL:try"  # Error handling start
    CTL_CATCH = "CTL:catch"  # Error handler
    CTL_FINALLY = "CTL:finally"  # Cleanup block

    # Data type tokens
    TYPE_STR = "TYPE:str"  # String type
    TYPE_INT = "TYPE:int"  # Integer type
    TYPE_FLOAT = "TYPE:float"  # Float type
    TYPE_BOOL = "TYPE:bool"  # Boolean type
    TYPE_LIST = "TYPE:list"  # List type
    TYPE_DICT = "TYPE:dict"  # Dictionary type
    TYPE_ANY = "TYPE:any"  # Any type

    # Error handling tokens
    ERR_RETRY = "ERR:retry"  # Retry operation
    ERR_FAIL = "ERR:fail"  # Fail operation
    ERR_LOG = "ERR:log"  # Log error
    ERR_IGNORE = "ERR:ignore"  # Ignore error

    # Modifiers
    MOD_ASYNC = "MOD:async"  # Async operation
    MOD_BATCH = "MOD:batch"  # Batch operation
    MOD_PARALLEL = "MOD:parallel"  # Parallel execution
    MOD_CACHED = "MOD:cached"  # Use cached value


@dataclass
class Token:
    """
    A single MoltLang token.

    Attributes:
        type: The token type
        value: Optional value associated with the token
        position: Position in the token sequence
    """

    type: TokenType
    value: str | None = None
    position: int = 0

    def __str__(self) -> str:
        """Return the string representation of the token."""
        if self.value:
            return f"[{self.type.value}={self.value}]"
        return f"[{self.type.value}]"

    def __len__(self) -> int:
        """Return the token length (always 1 for MoltLang tokens)."""
        return 1


@dataclass
class TokenSequence:
    """
    A sequence of MoltLang tokens.

    Attributes:
        tokens: List of tokens in the sequence
        metadata: Optional metadata about the sequence
    """

    tokens: list[Token] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        """Return the string representation of the token sequence."""
        return "".join(str(token) for token in self.tokens)

    def __len__(self) -> int:
        """Return the number of tokens in the sequence."""
        return len(self.tokens)

    def add(self, token: Token) -> "TokenSequence":
        """Add a token to the sequence."""
        token.position = len(self.tokens)
        self.tokens.append(token)
        return self

    def token_count(self) -> int:
        """Return the total token count."""
        return len(self.tokens)

    def compare_token_efficiency(self, english_word_count: int) -> float:
        """
        Compare token efficiency against English word count.

        Args:
            english_word_count: Number of words in English equivalent

        Returns:
            Token reduction percentage (0.0-1.0)
        """
        if english_word_count == 0:
            return 0.0
        return 1.0 - (self.token_count() / english_word_count)


class TokenRegistry:
    """
    Registry for managing MoltLang tokens.

    Provides methods for looking up tokens, managing custom tokens,
    and validating token sequences.
    """

    _instance: "TokenRegistry | None" = None
    _tokens: dict[str, Token] = None

    def __new__(cls) -> "TokenRegistry":
        """Singleton pattern for token registry."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        """Initialize the token registry with default tokens."""
        # Initialize _tokens as a mutable dict
        self._tokens = {}
        # Initialize _custom_tokens as a mutable dict
        self._custom_tokens = {}
        # Register all TokenType values as tokens
        for token_type in TokenType:
            self._tokens[token_type.value] = Token(type=token_type)

    def get(self, token_str: str) -> Token | None:
        """
        Get a token by its string representation (case-insensitive).

        Args:
            token_str: String representation of the token (e.g., "[OP:FETCH]" or "[OP:fetch]")

        Returns:
            Token if found, None otherwise
        """
        # Strip brackets if present
        clean = token_str.strip("[]")
        if "=" in clean:
            clean = clean.split("=")[0]

        # Try exact match first
        if clean in self._tokens:
            return self._tokens[clean]

        # Try case-insensitive match for LLM-friendliness
        clean_lower = clean.lower()
        for key, token in self._tokens.items():
            if key.lower() == clean_lower:
                return token

        # Check custom tokens
        if clean in self._custom_tokens:
            return self._custom_tokens[clean]

        return None

    def register_custom(self, name: str, token_type: TokenType) -> Token:
        """
        Register a custom token.

        Args:
            name: Name of the custom token
            token_type: Type of the token

        Returns:
            The registered token
        """
        token = Token(type=token_type, value=name)
        self._custom_tokens[f"{token_type.value}:{name}"] = token
        return token

    def list_tokens(self, token_type: TokenType | None = None) -> list[Token]:
        """
        List all tokens, optionally filtered by type.

        Args:
            token_type: Optional token type filter

        Returns:
            List of tokens
        """
        all_tokens = {**self._tokens, **self._custom_tokens}
        if token_type:
            return [t for t in all_tokens.values() if t.type == token_type]
        return list(all_tokens.values())

    def validate_sequence(self, sequence: TokenSequence) -> bool:
        """
        Validate a token sequence.

        Args:
            sequence: Token sequence to validate

        Returns:
            True if valid, False otherwise
        """
        for token in sequence.tokens:
            if token not in self._tokens.values() and token not in self._custom_tokens.values():
                return False
        return True


# Convenience functions for common operations

def op(operation: str) -> Token:
    """Create an operation token."""
    return Token(type=TokenType[f"OP_{operation.upper()}"])


def src(source: str) -> Token:
    """Create a source token."""
    return Token(type=TokenType[f"SRC_{source.upper()}"])


def param(param_type: str) -> Token:
    """Create a parameter token."""
    return Token(type=TokenType[f"PARAM_{param_type.upper()}"])


def ret(return_type: str) -> Token:
    """Create a return type token."""
    return Token(type=TokenType[f"RET_{return_type.upper()}"])


def sequence(*tokens: Token) -> TokenSequence:
    """Create a token sequence from tokens."""
    seq = TokenSequence()
    for token in tokens:
        seq.add(token)
    return seq
