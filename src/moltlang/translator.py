"""
MoltLang translation module.

This module provides bidirectional translation between English (and other human languages)
and MoltLang, the AI-optimized language.
"""

from dataclasses import dataclass
from typing import Any

from moltlang.config import MoltConfig, get_config
from moltlang.tokens import Token, TokenSequence, TokenType


@dataclass
class DetectedToken:
    """Token with position information for semantic grouping."""
    token: Token
    position: int  # Character position in original text
    keyword: str   # The keyword that triggered detection


@dataclass
class TranslationResult:
    """
    Result of a translation operation.

    Attributes:
        text: The translated text
        tokens: Token sequence (for MoltLang output)
        token_count: Number of tokens used
        confidence: Translation confidence score (0.0-1.0)
        original_token_count: Original token count (for efficiency calculation)
    """

    text: str
    tokens: TokenSequence | None = None
    token_count: int = 0
    confidence: float = 0.0
    original_token_count: int = 0

    @property
    def token_efficiency(self) -> float:
        """Calculate token efficiency (reduction percentage)."""
        if self.original_token_count == 0:
            return 0.0
        return 1.0 - (self.token_count / self.original_token_count)

    def __str__(self) -> str:
        """Return the translated text."""
        return self.text


class MoltTranslator:
    """
    Translator for MoltLang.

    Handles bidirectional translation between human languages and MoltLang.
    """

    def __init__(self, config: MoltConfig | None = None):
        """
        Initialize the translator.

        Args:
            config: Optional configuration. Uses default if not provided.
        """
        self.config = config or get_config()
        self._translation_cache: dict[str, TranslationResult] = {}

    def translate_to_molt(
        self, text: str, config: MoltConfig | None = None
    ) -> TranslationResult:
        """
        Translate human language text to MoltLang.

        Args:
            text: Human language text to translate
            config: Optional configuration override

        Returns:
            TranslationResult containing the MoltLang translation

        Examples:
            >>> translator = MoltTranslator()
            >>> result = translator.translate_to_molt("Fetch data from API")
            >>> print(result.text)
            [OP:FETCH][SRC:API]
        """
        cfg = config or self.config

        # Check cache
        if cfg.enable_cache and text in self._translation_cache:
            return self._translation_cache[text]

        # Tokenize input
        original_tokens = self._count_word_tokens(text)

        # Analyze and translate
        tokens = self._analyze_and_translate(text)

        # Build result
        result = TranslationResult(
            text=str(tokens),
            tokens=tokens,
            token_count=len(tokens),
            confidence=self._calculate_confidence(text, tokens),
            original_token_count=original_tokens,
        )

        # Cache result
        if cfg.enable_cache:
            self._translation_cache[text] = result

        return result

    def translate_from_molt(
        self, molt_text: str, config: MoltConfig | None = None
    ) -> TranslationResult:
        """
        Translate MoltLang to human language text.

        Args:
            molt_text: MoltLang text to translate
            config: Optional configuration override

        Returns:
            TranslationResult containing the human language translation

        Examples:
            >>> translator = MoltTranslator()
            >>> result = translator.translate_from_molt("[OP:FETCH][SRC:API]")
            >>> print(result.text)
            Fetch data from API
        """
        cfg = config or self.config

        # Parse MoltLang tokens
        tokens = self._parse_molt_tokens(molt_text)

        # Generate human language translation
        translation = self._generate_human_translation(tokens, cfg.human_language)

        return TranslationResult(
            text=translation,
            tokens=tokens,
            token_count=len(tokens),
            confidence=self._calculate_confidence(translation, tokens),
        )

    def _count_word_tokens(self, text: str) -> int:
        """Count word tokens in text."""
        return len(text.split())

    def _analyze_and_translate(self, text: str) -> TokenSequence:
        """
        Analyze human text and generate MoltLang tokens with semantic grouping.

        LLM-Friendly: Supports multiple operations, modifiers, and parameters.
        Uses position-based semantic grouping to associate sources/returns with operations.
        """
        # Step 1: Detect all tokens with positions
        detected = self._detect_with_positions(text)

        # Step 2: Build semantic groups
        groups = self._build_semantic_groups(text, detected)

        # Step 3: Flatten to final sequence
        tokens = self._flatten_groups(detected, groups)

        # Step 4: Apply fallback rules
        return self._apply_fallback_rules(text, tokens)

    def _detect_with_positions(self, text: str) -> dict[str, list[DetectedToken]]:
        """Detect all tokens with their positions in text."""
        import re
        text_lower = text.lower()
        detected = {
            "modifiers": [],
            "control": [],
            "errors": [],
            "operations": [],
            "sources": [],
            "returns": [],
            "params": [],
            "types": [],
        }

        # MODIFIER detection
        # Check for "multiple X" where X is a source - don't add MOD:batch
        multiple_source_pattern = re.search(r'multiple\s+(?:apis?|sources?|endpoints?)', text_lower)

        mod_keywords = {
            TokenType.MOD_ASYNC: ["async", "asynchronous", "asyncronously"],
            TokenType.MOD_PARALLEL: ["parallel", "concurrent", "simultaneous"],
            TokenType.MOD_BATCH: ["batch", "bulk"],  # "multiple" excluded when followed by sources
            TokenType.MOD_CACHED: ["cache", "cached", "caching"],
        }
        for token_type, keywords in mod_keywords.items():
            # Skip MOD_BATCH for "multiple APIs" pattern
            if token_type == TokenType.MOD_BATCH and multiple_source_pattern:
                # Check if keywords would match "multiple" - skip if so
                if "multiple" in keywords:
                    continue
            for keyword in keywords:
                pos = text_lower.find(keyword)
                if pos != -1:
                    detected["modifiers"].append(DetectedToken(
                        token=Token(type=token_type),
                        position=pos,
                        keyword=keyword
                    ))
                    break

        # CONTROL FLOW detection
        has_error_context = any(err in text_lower for err in ["error", "fail", "exception"])
        # Also check for "otherwise" pattern - only CTL_ELSE if NOT in "otherwise log" pattern
        otherwise_in_log_pattern = "otherwise" in text_lower and any(word in text_lower for word in ["log", "record", "print"])

        ctl_keywords = {
            TokenType.CTL_TRY: ["try", "attempt", "attempting", "trying to", "give it a shot"],
            TokenType.CTL_CATCH: ["catch", "handle error", "on error", "except", "when error", "on failure", "error handler"],
            TokenType.CTL_FINALLY: ["finally", "cleanup", "afterwards", "always do"],
            TokenType.CTL_IF: ["if", "conditional", "when", "whenever", "in case", "depending on"],
            TokenType.CTL_ELSE: ["else", "alternative", "or else", "fallback"],  # "otherwise" excluded if followed by log
            TokenType.CTL_LOOP: ["loop", "iterate", "repeat", "cycle", "for each", "while"],
        }
        for token_type, keywords in ctl_keywords.items():
            # Skip CTL_IF in error context
            if token_type == TokenType.CTL_IF and has_error_context:
                continue
            # Skip CTL_ELSE if in "otherwise log" pattern
            if token_type == TokenType.CTL_ELSE and otherwise_in_log_pattern:
                continue
            for keyword in keywords:
                pos = text_lower.find(keyword)
                if pos != -1:
                    detected["control"].append(DetectedToken(
                        token=Token(type=token_type),
                        position=pos,
                        keyword=keyword
                    ))
                    break

        # ERROR HANDLING detection
        # Check for "on failure" pattern - don't add ERR:FAIL for this
        on_failure_pattern = "on failure" in text_lower or "on error" in text_lower

        err_keywords = {
            TokenType.ERR_RETRY: ["retry", "try again", "reattempt", "attempt again", "keep trying"],
            TokenType.ERR_LOG: ["log", "logging", "record", "write log", "log entry", "log error"],
            TokenType.ERR_FAIL: ["fail", "throw error", "raise error", "abort on error"],  # "failure" excluded if in "on failure"
            TokenType.ERR_IGNORE: ["ignore", "skip error", "continue on error", "suppress error"],
        }
        for token_type, keywords in err_keywords.items():
            for keyword in keywords:
                # Skip ERR:FAIL detection for "failure" in "failed records" or "on failure" context
                if token_type == TokenType.ERR_FAIL:
                    if "failed" in text_lower or "on failure" in text_lower:
                        # Only add if explicit "fail" keyword (not "failed" or "failure")
                        if keyword == "fail" and re.search(r'\bfail\b', text_lower):
                            pos = text_lower.find(keyword)
                            if pos != -1:
                                detected["errors"].append(DetectedToken(
                                    token=Token(type=token_type),
                                    position=pos,
                                    keyword=keyword
                                ))
                        continue
                pos = text_lower.find(keyword)
                if pos != -1:
                    detected["errors"].append(DetectedToken(
                        token=Token(type=token_type),
                        position=pos,
                        keyword=keyword
                    ))
                    break

        # OPERATION detection - support MULTIPLE operations
        # Check for "ensure X returns" pattern - this should NOT be OP:validate
        ensure_returns_pattern = re.search(r'ensure\s+(?:it\s+)?returns?', text_lower)

        op_keywords = {
            TokenType.OP_FETCH: ["fetch", "get", "retrieve", "download"],
            TokenType.OP_PARSE: ["parse", "analyze", "extract"],
            TokenType.OP_TRANSFORM: ["transform", "convert", "change"],
            TokenType.OP_SEARCH: ["search", "find", "lookup"],
            TokenType.OP_VALIDATE: ["validate", "verify"],  # "check" and "ensure" excluded in some contexts
            TokenType.OP_FILTER: ["filter", "sift", "screen"],
            TokenType.OP_AGGREGATE: ["aggregate", "combine", "merge", "summarize"],
            TokenType.OP_PROCESS: ["process", "handle"],
        }
        for token_type, keywords in op_keywords.items():
            # Skip OP_VALIDATE if in "ensure returns" context
            if token_type == TokenType.OP_VALIDATE and ensure_returns_pattern:
                # Still check for validate/verify but not check/ensure
                keywords = [k for k in keywords if k not in ["check", "ensure"]]
            for keyword in keywords:
                pos = text_lower.find(keyword)
                if pos != -1:
                    detected["operations"].append(DetectedToken(
                        token=Token(type=token_type),
                        position=pos,
                        keyword=keyword
                    ))
                    break  # Only first match per operation type

        # Default to COMPUTE if no operation found (unless question)
        if not detected["operations"]:
            if text.strip().endswith("?"):
                detected["operations"].append(DetectedToken(
                    token=Token(type=TokenType.OP_SEARCH),
                    position=0,
                    keyword="?"
                ))
            else:
                detected["operations"].append(DetectedToken(
                    token=Token(type=TokenType.OP_COMPUTE),
                    position=0,
                    keyword="compute"
                ))

        # SOURCE detection
        src_keywords = {
            TokenType.SRC_API: ["api", "endpoint", "rest", "graphql"],
            TokenType.SRC_DB: ["database", "db", "sql", "nosql"],
            TokenType.SRC_FILE: ["file", "csv", "json file", "data file"],
            TokenType.SRC_MEM: ["memory", "cache", "ram"],
        }
        for token_type, keywords in src_keywords.items():
            for keyword in keywords:
                pos = text_lower.find(keyword)
                if pos != -1:
                    detected["sources"].append(DetectedToken(
                        token=Token(type=token_type),
                        position=pos,
                        keyword=keyword
                    ))
                    break

        # PARAMETER detection - extract values with regex
        # Check for ID/key patterns first (more specific)
        param_patterns = [
            # ID detection (most specific - "ID 12345", "user ID 12345")
            (TokenType.PARAM_KEY, r'(?:user\s+)?(?:id|identifier)\s*(?:of|:|=)?\s*(\d+[\w-]*)', 'id'),
            # API key detection
            (TokenType.PARAM_KEY, r'(?:api\s+)?key\s*(?:of|:|=)?\s*["\']?([\w-]+)["\']?', 'key'),
            # Times/retry count - handle "retry X times" or "retry ... X times"
            (TokenType.PARAM_TIMES, r'(?:retry|repeat)\s+(?:.*?)?(\d+)\s+times?', 'times'),
            (TokenType.PARAM_TIMEOUT, r'timeout\s*(?:of|:|=)?\s*(\d+)\s*(?:seconds?|secs?|s)?', 'timeout'),
            (TokenType.PARAM_TIMEOUT, r'timeout\s*(?:of|:|=)?\s*(\d+)\s*(?:seconds?|secs?|s)?', 'timeout'),
            # Limit - handle "X records" or "limit X"
            (TokenType.PARAM_LIMIT, r'(?:process|batch|handle)\s+(\d+)\s+(?:records?|items?|entries?)', 'limit'),
            (TokenType.PARAM_LIMIT, r'(?:limit|max|maximum)\s*(?:of|:|=)?\s*(\d+)|(?:at\s+most)\s*(\d+)', 'limit2'),
            (TokenType.PARAM_OFFSET, r'(?:offset|skip)\s*(?:of|:|=)?\s*(\d+)', 'offset'),
            # Token/auth
            (TokenType.PARAM_TOKEN, r'(?:auth|bearer|access)?\s*token\s*(?:of|:|=)?\s*["\']?([\w.-]+)["\']?', 'token'),
            # Query (least specific - check last) - capture only up to next delimiter
            # Exclude when "search" is followed by database/api/file (sources)
            (TokenType.PARAM_QUERY, r'(?:query|find)\s+(?:for|:|=)?\s*["\']?([^"\']{1,30}?)(?:["\']|,|\.|and)\s', 'query'),
        ]
        for token_type, pattern, name in param_patterns:
            match = re.search(pattern, text_lower)
            if match:
                # Handle PARAM_LIMIT which has two groups
                if token_type == TokenType.PARAM_LIMIT:
                    value = match.group(1) if match.group(1) else match.group(2)
                    # For limit2, use the position of the matched group
                    if name == 'limit2' and match.group(2):
                        param_pos = text_lower.find(match.group(2), match.start())
                    else:
                        param_pos = match.start()
                elif name == 'id':
                    value = match.group(1)
                    param_pos = match.start()
                elif name == 'times':
                    value = match.group(1)
                    # For PARAM:TIMES, find the position of the number (not the start of "retry")
                    param_pos = text_lower.find(match.group(1), match.start())
                else:
                    value = match.group(1) if match.lastindex and match.group(1) else None
                    param_pos = match.start()
                detected["params"].append(DetectedToken(
                    token=Token(type=token_type, value=value),
                    position=param_pos,
                    keyword=match.group(0)
                ))

        # RETURN type detection - IMPORTANT: detect ALL occurrences
        ret_keywords = {
            TokenType.RET_JSON: ["json", "object"],
            TokenType.RET_TEXT: ["csv", "text", "plain"],
            TokenType.RET_LIST: ["list", "array"],
            TokenType.RET_DICT: ["dictionary", "dict", "map"],
            TokenType.RET_BOOL: ["boolean", "bool", "true", "false"],
            TokenType.RET_NUM: ["number", "numeric"],
        }
        for token_type, keywords in ret_keywords.items():
            for keyword in keywords:
                # Find ALL occurrences, not just first
                start = 0
                found = False
                while True:
                    pos = text_lower.find(keyword, start)
                    if pos == -1:
                        break
                    detected["returns"].append(DetectedToken(
                        token=Token(type=token_type),
                        position=pos,
                        keyword=keyword
                    ))
                    start = pos + 1
                    found = True
                if found:
                    break  # Only use first matching keyword set per type

        # TYPE constraint detection - only explicit "type X" patterns, not return keywords
        # Filter out TYPE tokens that overlap with RETURN tokens (avoid duplicates)
        ret_positions = {ret.position for ret in detected["returns"]}

        # Special pattern: "list of strings" or "list of <type>" should add TYPE constraint
        list_of_match = re.search(r'list\s+(?:of\s+)?(?:strings?|ints?|floats?|strs?|texts?|booleans?)', text_lower)
        if list_of_match and "list" not in {rt.position for rt in detected["returns"]}:
            # Extract the type from the match
            matched_text = list_of_match.group(0).lower()
            if "string" in matched_text or "str" in matched_text or "text" in matched_text:
                # Add TYPE:str at the position of the type word
                type_pos = text_lower.find("string", list_of_match.start())
                if type_pos == -1:
                    type_pos = text_lower.find("str", list_of_match.start())
                if type_pos != -1:
                    detected["types"].append(DetectedToken(
                        token=Token(type=TokenType.TYPE_STR),
                        position=type_pos,
                        keyword="string"
                    ))

        type_keywords = {
            TokenType.TYPE_STR: ["type str", "type string", "string type", "typed list of strings", r'\btype\s*[:=]\s*str(?:ing)?\b'],
            TokenType.TYPE_INT: ["type int", "integer type", "as integer", "to integer", r'\btype\s*[:=]\s*int(?:eger)?\b'],
            TokenType.TYPE_FLOAT: ["type float", "float type", "decimal type", r'\btype\s*[:=]\s*float\b'],
            TokenType.TYPE_BOOL: ["type bool", "boolean type", "as boolean", r'\btype\s*[:=]\s*bool(?:ean)?\b'],
            TokenType.TYPE_LIST: ["type list", "list type", "array type", "as list", "to list", r'\btype\s*[:=]\s*list\b'],
            TokenType.TYPE_DICT: ["type dict", "dict type", "map type", "as dict", "to dict", r'\btype\s*[:=]\s*dict\b'],
            TokenType.TYPE_ANY: ["type any", "any type", r'\btype\s*[:=]\s*any\b'],
        }
        for token_type, keywords in type_keywords.items():
            for keyword in keywords:
                if keyword.startswith(r'\b'):  # Regex pattern
                    match = re.search(keyword, text_lower)
                    if match and match.start() not in ret_positions:
                        detected["types"].append(DetectedToken(
                            token=Token(type=token_type),
                            position=match.start(),
                            keyword=keyword
                        ))
                        break
                else:
                    pos = text_lower.find(keyword)
                    if pos != -1 and pos not in ret_positions:
                        detected["types"].append(DetectedToken(
                            token=Token(type=token_type),
                            position=pos,
                            keyword=keyword
                        ))
                        break

        return detected

    def _build_semantic_groups(self, text: str, detected: dict) -> list[dict]:
        """Build operation groups based on text position."""
        import re
        text_lower = text.lower()

        # Sort operations by position
        operations = sorted(detected["operations"], key=lambda x: x.position)
        sources = sorted(detected["sources"], key=lambda x: x.position)
        # Deduplicate returns by token type (keep first occurrence of each type)
        unique_returns = {}
        for ret in detected["returns"]:
            if ret.token.type not in unique_returns:
                unique_returns[ret.token.type] = ret
        returns = sorted(unique_returns.values(), key=lambda x: x.position)
        params = sorted(detected["params"], key=lambda x: x.position)

        groups = []
        used_sources = set()
        used_returns = set()
        used_params = set()

        # Detect "return as <type>" or "return <type>" pattern for final return
        final_return = None
        final_return_pos = len(text_lower)
        return_match = re.search(r'return\s+(?:as\s+)?(?:a\s+)?(\w+)', text_lower)
        if return_match:
            return_type = return_match.group(1)
            # Map return type to token
            return_map = {
                "json": TokenType.RET_JSON, "object": TokenType.RET_JSON,
                "csv": TokenType.RET_TEXT, "text": TokenType.RET_TEXT, "plain": TokenType.RET_TEXT,
                "list": TokenType.RET_LIST, "array": TokenType.RET_LIST,
                "dict": TokenType.RET_DICT, "dictionary": TokenType.RET_DICT, "map": TokenType.RET_DICT,
                "bool": TokenType.RET_BOOL, "boolean": TokenType.RET_BOOL,
                "number": TokenType.RET_NUM, "numeric": TokenType.RET_NUM,
            }
            if return_type in return_map:
                final_return = Token(type=return_map[return_type])
                final_return_pos = return_match.start()

        for i, op in enumerate(operations):
            group = {
                "operation": op.token,
                "source": None,
                "returns": [],
                "params": []
            }

            # Find nearest source BEFORE this operation (or first op gets first source)
            if i == 0 and sources:
                # First operation gets the source
                group["source"] = sources[0].token
                used_sources.add(0)
            else:
                # Check for source between previous op and this one
                prev_pos = operations[i-1].position if i > 0 else 0
                for j, src in enumerate(sources):
                    if j not in used_sources and prev_pos < src.position <= op.position:
                        group["source"] = src.token
                        used_sources.add(j)
                        break

            # Find returns that are "near" this operation
            next_op_pos = operations[i+1].position if i+1 < len(operations) else len(text_lower)

            for j, ret in enumerate(returns):
                if j not in used_returns:
                    # Skip if this is the final return (belongs to last operation)
                    if abs(ret.position - final_return_pos) < 5:
                        continue
                    # Check for explicit "to <type>" pattern with this operation
                    if f"{op.keyword} to" in text_lower or f"{op.keyword}s to" in text_lower:
                        to_pos = text_lower.find(" to ", op.position)
                        if to_pos != -1 and to_pos < next_op_pos:
                            if to_pos < ret.position < to_pos + 20:
                                group["returns"].append(ret.token)
                                used_returns.add(j)
                    # Otherwise, only assign return to first operation if it's very close
                    elif i == 0 and ret.position < op.position + 30:
                        # First operation gets returns that appear early
                        group["returns"].append(ret.token)
                        used_returns.add(j)

            # Find params that are "near" this operation
            # Exception: PARAM:times that comes after ERR:retry should NOT be added to operation group
            err_retry_positions = [e.position for e in detected["errors"] if e.token.type == TokenType.ERR_RETRY]

            for j, param in enumerate(params):
                if j not in used_params:
                    # Skip PARAM:times if it comes after ERR:retry (belongs with error handling)
                    if param.token.type == TokenType.PARAM_TIMES:
                        # Check if there's an ERR:retry before this param
                        if any(err_pos < param.position for err_pos in err_retry_positions):
                            # Mark as used so it doesn't get added by "Handle remaining params"
                            used_params.add(j)
                            continue  # Don't add to operation group
                    if op.position <= param.position < next_op_pos:
                        group["params"].append(param.token)
                        used_params.add(j)

            groups.append(group)

        # Assign final return to last operation (but only if not already added)
        if groups and final_return:
            # Check if this return type is already in the last group
            last_return_types = {r.type for r in groups[-1]["returns"]}
            if final_return.type not in last_return_types:
                groups[-1]["returns"].append(final_return)
            # Mark returns near final_return_pos as used
            for j, ret in enumerate(returns):
                if abs(ret.position - final_return_pos) < 5:
                    used_returns.add(j)

        # Handle remaining returns - assign to last operation
        if groups:
            for j, ret in enumerate(returns):
                if j not in used_returns:
                    # Check if this return type is already in the last group
                    last_return_types = {r.type for r in groups[-1]["returns"]}
                    if ret.token.type not in last_return_types:
                        groups[-1]["returns"].append(ret.token)

        # Handle remaining params - assign to last operation
        if groups:
            for j, param in enumerate(params):
                if j not in used_params:
                    groups[-1]["params"].append(param.token)

        return groups

    def _flatten_groups(self, detected: dict, groups: list[dict]) -> TokenSequence:
        """Flatten semantic groups into final token sequence.

        Token ordering follows semantic flow:
        1. CTL:try (if present) - comes first
        2. MOD:async, MOD:batch, MOD:parallel (operation modifiers, sorted by type priority)
        3. Operation groups (OP + SRC + PARAM + RET)
        4. MOD:cached (can come after operation)
        5. CTL:catch, CTL:finally (error handling blocks)
        6. ERR:retry, ERR:log (error handling actions)
        7. TYPE constraints
        """
        tokens = TokenSequence()

        # Separate control flow tokens
        try_tokens = [dt for dt in detected["control"] if dt.token.type == TokenType.CTL_TRY]
        catch_tokens = [dt for dt in detected["control"] if dt.token.type == TokenType.CTL_CATCH]
        finally_tokens = [dt for dt in detected["control"] if dt.token.type == TokenType.CTL_FINALLY]
        other_ctl_tokens = [dt for dt in detected["control"] if dt.token.type not in [TokenType.CTL_TRY, TokenType.CTL_CATCH, TokenType.CTL_FINALLY]]

        # Separate modifiers - cached can come after operation, sort others by text position
        cached_mods = [dt for dt in detected["modifiers"] if dt.token.type == TokenType.MOD_CACHED]
        other_mods = [dt for dt in detected["modifiers"] if dt.token.type != TokenType.MOD_CACHED]
        # Sort modifiers by text position (maintains order as they appear in text)
        other_mods.sort(key=lambda dt: dt.position)

        # Separate error tokens - fail should only be explicit
        # Also extract any PARAM:times that should come with ERR:retry
        err_tokens = []
        times_params = []
        for dt in detected["errors"]:
            if dt.token.type == TokenType.ERR_RETRY:
                err_tokens.append(dt)
                # Find associated PARAM:times
                for pt in detected["params"]:
                    if pt.token.type == TokenType.PARAM_TIMES and pt.position > dt.position:
                        times_params.append(pt)
                        break
            else:
                err_tokens.append(dt)
        # Remove times params from regular params list (they'll be added with error tokens)
        detected_params_for_groups = [pt for pt in detected["params"] if pt not in times_params]

        # Collect all return types used in groups to filter out duplicate TYPE tokens
        used_return_types = set()
        for group in groups:
            for ret in group["returns"]:
                ret_to_type_map = {
                    TokenType.RET_JSON: TokenType.TYPE_STR,
                    TokenType.RET_TEXT: TokenType.TYPE_STR,
                    TokenType.RET_LIST: TokenType.TYPE_LIST,
                    TokenType.RET_DICT: TokenType.TYPE_DICT,
                    TokenType.RET_BOOL: TokenType.TYPE_BOOL,
                    TokenType.RET_NUM: TokenType.TYPE_INT,
                }
                if ret.type in ret_to_type_map:
                    used_return_types.add(ret_to_type_map[ret.type])

        # 1. CTL:try first (if present)
        for dt in try_tokens:
            tokens.add(dt.token)

        # 2. Other modifiers (batch, parallel, async) - sorted by priority
        for dt in other_mods:
            tokens.add(dt.token)

        # 3. Other control flow (if, else, loop)
        for dt in other_ctl_tokens:
            tokens.add(dt.token)

        # 4. Error handling (retry, log, etc.) - but save some for after catch
        # Split: retry/log can go before or after catch depending on context
        main_err_tokens = []
        post_catch_err_tokens = []
        for dt in err_tokens:
            # ERR:retry and ERR:log typically come after CTL:catch
            if dt.token.type in [TokenType.ERR_RETRY, TokenType.ERR_LOG]:
                post_catch_err_tokens.append(dt)
            else:
                main_err_tokens.append(dt)

        # 5. Operation groups in order
        for group in groups:
            tokens.add(group["operation"])
            if group["source"]:
                tokens.add(group["source"])
            for param in group["params"]:
                tokens.add(param)
            for ret in group["returns"]:
                tokens.add(ret)

        # 6. MOD:cached (can come after operation)
        for dt in cached_mods:
            tokens.add(dt.token)

        # 7. CTL:catch - add implicitly if we have try + error handling but no explicit catch
        has_try = len(try_tokens) > 0
        has_explicit_catch = len(catch_tokens) > 0
        has_error_handling = len(post_catch_err_tokens) > 0

        if has_try and has_error_handling and not has_explicit_catch:
            # Add implicit CTL:catch
            tokens.add(Token(type=TokenType.CTL_CATCH))

        for dt in catch_tokens:
            tokens.add(dt.token)
        for dt in finally_tokens:
            tokens.add(dt.token)

        # 8. Post-catch error tokens (retry, log) and their associated params
        for dt in post_catch_err_tokens:
            tokens.add(dt.token)
            # Add PARAM:times if it's associated with this ERR:retry
            if dt.token.type == TokenType.ERR_RETRY:
                for pt in detected["params"]:
                    if pt.token.type == TokenType.PARAM_TIMES and pt.position > dt.position:
                        tokens.add(pt.token)
                        break

        # 9. Other error tokens
        for dt in main_err_tokens:
            tokens.add(dt.token)

        # 10. Type constraints at end - filter out if return type already used, also deduplicate
        seen_types = set()
        for dt in detected["types"]:
            if dt.token.type not in used_return_types and dt.token.type not in seen_types:
                tokens.add(dt.token)
                seen_types.add(dt.token.type)

        return tokens

    def _parse_molt_tokens(self, molt_text: str) -> TokenSequence:
        """
        Parse MoltLang text into tokens.

        LLM-friendly: Case-insensitive parsing for flexibility.
        Accepts both [RET:JSON] and [RET:json] - normalizes to enum values.

        Args:
            molt_text: MoltLang string representation

        Returns:
            TokenSequence containing parsed tokens
        """
        tokens = TokenSequence()
        import re

        # Find all token patterns like [TYPE:VALUE] - case-insensitive
        pattern = r"\[([a-zA-Z]+):([a-zA-Z_0-9]+)(?:=([^\]]+))?\]"
        matches = re.findall(pattern, molt_text)

        for category, value, param in matches:
            # Normalize to uppercase for enum lookup
            token_type_str = f"{category.upper()}_{value.upper()}"
            try:
                token_type = TokenType[token_type_str]
                token = Token(type=token_type, value=param if param else None)
                tokens.add(token)
            except KeyError:
                # Unknown token type, skip or handle as custom
                pass

        return tokens

    def _generate_human_translation(
        self, tokens: TokenSequence, target_language: str = "en"
    ) -> str:
        """
        Generate human language translation from MoltLang tokens.

        Args:
            tokens: TokenSequence to translate
            target_language: Target human language (default: English)

        Returns:
            Human language translation
        """
        parts: list[str] = []

        for token in tokens.tokens:
            # Operation translations
            if token.type == TokenType.OP_FETCH:
                parts.append("Fetch")
            elif token.type == TokenType.OP_PARSE:
                parts.append("Parse")
            elif token.type == TokenType.OP_TRANSFORM:
                parts.append("Transform")
            elif token.type == TokenType.OP_SEARCH:
                parts.append("Search")
            elif token.type == TokenType.OP_VALIDATE:
                parts.append("Validate")
            elif token.type == TokenType.OP_FILTER:
                parts.append("Filter")
            elif token.type == TokenType.OP_COMPUTE:
                parts.append("Compute")

            # Source translations
            elif token.type == TokenType.SRC_API:
                parts.append("data from API")
            elif token.type == TokenType.SRC_DB:
                parts.append("data from database")
            elif token.type == TokenType.SRC_FILE:
                parts.append("data from file")
            elif token.type == TokenType.SRC_MEM:
                parts.append("data from memory")

            # Return type translations
            elif token.type == TokenType.RET_JSON:
                parts.append("return JSON")
            elif token.type == TokenType.RET_TEXT:
                parts.append("return text")
            elif token.type == TokenType.RET_BOOL:
                parts.append("return boolean")
            elif token.type == TokenType.RET_NUM:
                parts.append("return number")
            elif token.type == TokenType.RET_LIST:
                parts.append("return list")
            elif token.type == TokenType.RET_DICT:
                parts.append("return dictionary")

        return " ".join(parts) if parts else "Empty operation"

    def _calculate_confidence(self, original: str, tokens: TokenSequence) -> float:
        """
        Calculate translation confidence score.

        Enhanced to consider semantic completeness, not just token count.

        Args:
            original: Original text
            tokens: Translated token sequence

        Returns:
            Confidence score (0.0-1.0)
        """
        if len(tokens) == 0:
            return 0.0

        # Base score from token count (capped at 0.7 for 3+ tokens)
        base_score = min(0.7, 0.5 + (len(tokens) * 0.1))

        # Semantic completeness bonus (only if complete)
        has_operation = any("OP:" in t.type.value for t in tokens.tokens)
        has_source = any("SRC:" in t.type.value for t in tokens.tokens)
        has_return = any("RET:" in t.type.value for t in tokens.tokens)

        completeness = 0.0
        # Only give bonus for complete operations (operation + source/return)
        if has_operation and (has_source or has_return):
            completeness += 0.25
        # Extra bonus for having both source AND return
        if has_operation and has_source and has_return:
            completeness += 0.15
        # Small bonus for having control flow or error handling
        has_ctl = any("CTL:" in t.type.value for t in tokens.tokens)
        has_err = any("ERR:" in t.type.value for t in tokens.tokens)
        if has_ctl or has_err:
            completeness += 0.05

        return round(min(1.0, base_score + completeness), 2)

    def _apply_fallback_rules(self, text: str, tokens: TokenSequence) -> TokenSequence:
        """
        Apply fallback rules when direct matching fails.

        This uses heuristics to infer likely tokens from context.

        Args:
            text: Original human language text
            tokens: Current token sequence

        Returns:
            Potentially modified token sequence
        """
        import re
        text_lower = text.lower()

        # Fallback 1: "safe" or "careful" implies error handling
        if any(word in text_lower for word in ["safe", "careful", "graceful", "handle"]):
            if not any(t.type.value.startswith("CTL:") for t in tokens.tokens):
                tokens.add(Token(type=TokenType.CTL_TRY))
                tokens.add(Token(type=TokenType.CTL_CATCH))

        # Fallback 2: "ensure" or "guarantee" implies validation
        # Exception: "ensure [it] returns" describes return type, not validation
        ensure_returns_pattern = re.search(r'ensure\s+(?:it\s+)?returns?', text_lower)
        if any(word in text_lower for word in ["ensure", "guarantee", "verify"]):
            # Skip if "ensure returns" pattern (describes return type, not validation)
            if not ensure_returns_pattern:
                if not any(t.type == TokenType.OP_VALIDATE for t in tokens.tokens):
                    tokens.add(Token(type=TokenType.OP_VALIDATE))

        # Fallback 3: Questions default to search
        if text.strip().endswith("?"):
            if not any(t.type.value.startswith("OP:") for t in tokens.tokens):
                tokens.add(Token(type=TokenType.OP_SEARCH))
        # Fallback 3b: Questions with source but no operation
        if text.strip().endswith("?"):
            has_source = any(t.type.value.startswith("SRC:") for t in tokens.tokens)
            has_operation = any(t.type.value.startswith("OP:") for t in tokens.tokens)
            if has_source and not has_operation:
                tokens.add(Token(type=TokenType.OP_SEARCH))

        return tokens


# Convenience functions for direct usage

_translator_instance: MoltTranslator | None = None


def _get_translator() -> MoltTranslator:
    """Get or create the shared translator instance."""
    global _translator_instance
    if _translator_instance is None:
        _translator_instance = MoltTranslator()
    return _translator_instance


def translate_to_molt(text: str, config: MoltConfig | None = None) -> str:
    """
    Translate human language text to MoltLang.

    This is a convenience function that uses a shared translator instance.

    Args:
        text: Human language text to translate
        config: Optional configuration override

    Returns:
        MoltLang string representation

    Examples:
        >>> from moltlang import translate_to_molt
        >>> molt = translate_to_molt("Fetch data from API and return JSON")
        >>> print(molt)
        [OP:FETCH][SRC:API][RET:JSON]
    """
    translator = _get_translator()
    result = translator.translate_to_molt(text, config)
    return result.text


def translate_from_molt(molt_text: str, config: MoltConfig | None = None) -> str:
    """
    Translate MoltLang to human language text.

    This is a convenience function that uses a shared translator instance.

    Args:
        molt_text: MoltLang text to translate
        config: Optional configuration override

    Returns:
        Human language translation

    Examples:
        >>> from moltlang import translate_from_molt
        >>> english = translate_from_molt("[OP:FETCH][SRC:API][RET:JSON]")
        >>> print(english)
        Fetch data from API return JSON
    """
    translator = _get_translator()
    result = translator.translate_from_molt(molt_text, config)
    return result.text
