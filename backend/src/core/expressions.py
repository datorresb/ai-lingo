"""Expression extraction and normalization module.

This module provides functionality to parse, extract, and normalize expressions
from text, including support for streaming operations. It handles the [[phrase::meaning]]
markup format used by the Expression Learner Agent.

Refer to PRD section 5.3 for detailed specifications.
"""

import re
from typing import Generator, Iterable, Optional
from src.core.models import Expression


# ============================================================================
# Constants
# ============================================================================

# Pattern to match [[phrase::meaning]] format
EXPRESSION_PATTERN = r'\[\[([^\[\]]+?)::([^\[\]]+?)\]\]'

# Minimum and maximum lengths for phrase and meaning
MIN_PHRASE_LENGTH = 1
MAX_PHRASE_LENGTH = 200
MIN_MEANING_LENGTH = 1
MAX_MEANING_LENGTH = 500

# Characters that should be removed from expression text
SPECIAL_CHARS_PATTERN = r'[\n\r\t]'


# ============================================================================
# Expression Validation
# ============================================================================


def validate_expression(phrase: str, meaning: str) -> bool:
    """Validate an expression for sanity checks.

    Validates that the phrase and meaning meet minimum requirements:
    - Non-empty after normalization
    - Within length constraints
    - Contains at least one letter or digit

    Args:
        phrase: The expression phrase to validate
        meaning: The expression meaning to validate

    Returns:
        True if expression is valid, False otherwise
    """
    # Check empty strings
    if not phrase or not meaning:
        return False

    # Check length constraints
    if not (MIN_PHRASE_LENGTH <= len(phrase) <= MAX_PHRASE_LENGTH):
        return False
    if not (MIN_MEANING_LENGTH <= len(meaning) <= MAX_MEANING_LENGTH):
        return False

    # Check that both contain at least one alphanumeric character
    phrase_has_alnum = any(c.isalnum() for c in phrase)
    meaning_has_alnum = any(c.isalnum() for c in meaning)

    return phrase_has_alnum and meaning_has_alnum


# ============================================================================
# Expression Normalization
# ============================================================================


def normalize_expression(phrase: str, meaning: str) -> tuple[str, str]:
    """Normalize an expression phrase and meaning.

    Normalization includes:
    - Stripping leading/trailing whitespace
    - Removing tab and newline characters
    - Standardizing internal whitespace (multiple spaces -> single space)
    - Preserving case

    Args:
        phrase: The expression phrase to normalize
        meaning: The expression meaning to normalize

    Returns:
        Tuple of (normalized_phrase, normalized_meaning)
    """
    # Remove newlines, carriage returns, and tabs
    phrase = re.sub(SPECIAL_CHARS_PATTERN, ' ', phrase)
    meaning = re.sub(SPECIAL_CHARS_PATTERN, ' ', meaning)

    # Strip leading/trailing whitespace
    phrase = phrase.strip()
    meaning = meaning.strip()

    # Normalize internal whitespace (multiple spaces to single)
    phrase = re.sub(r'\s+', ' ', phrase)
    meaning = re.sub(r'\s+', ' ', meaning)

    return phrase, meaning


# ============================================================================
# Complete Text Parsing
# ============================================================================


def parse_expressions(text: str) -> list[Expression]:
    """Parse complete text for all [[phrase::meaning]] expressions.

    Extracts all expressions from the provided text using regex pattern matching.
    Each match is normalized and validated before being returned.

    Args:
        text: The complete text to parse for expressions

    Returns:
        List of Expression objects found and validated in the text
    """
    expressions = []

    # Find all matches of the expression pattern
    for match in re.finditer(EXPRESSION_PATTERN, text):
        phrase, meaning = match.groups()

        # Normalize the extracted values
        phrase, meaning = normalize_expression(phrase, meaning)

        # Validate before adding
        if validate_expression(phrase, meaning):
            expressions.append(Expression(phrase=phrase, meaning=meaning))

    return expressions


# ============================================================================
# Streaming Parsing
# ============================================================================


class _StreamingExpressionBuffer:
    """Internal buffer for managing partial expressions during streaming.

    This class maintains state across streaming chunks to handle expressions
    that span multiple chunks.
    """

    def __init__(self) -> None:
        """Initialize the buffer."""
        self.buffer = ""
        self.start_idx = 0

    def add_chunk(self, chunk: str) -> tuple[str, int]:
        """Add a chunk and return the accumulated text for parsing.

        Args:
            chunk: The new text chunk to add

        Returns:
            Tuple of (accumulated_text, start_position_in_text)
        """
        self.buffer += chunk
        return self.buffer, self.start_idx

    def remove_processed(self, num_chars: int) -> None:
        """Remove processed characters from buffer.

        Args:
            num_chars: Number of characters to remove from the start
        """
        self.buffer = self.buffer[num_chars:]
        self.start_idx += num_chars

    def get_remaining(self) -> str:
        """Get remaining buffered content.

        Returns:
            Remaining unprocessed content
        """
        return self.buffer

    def clear(self) -> None:
        """Clear the buffer completely."""
        self.buffer = ""
        self.start_idx = 0


def stream_expressions(text_chunks: Iterable[str]) -> Generator[Expression, None, None]:
    """Parse streaming text chunks and yield complete expressions.

    This function processes text as it arrives in chunks, yielding expressions
    as soon as they are completely received. It handles partial expressions
    that span multiple chunks by maintaining an internal buffer.

    The function uses a greedy approach: it looks for complete expression markers
    ([[phrase::meaning]]) and yields them immediately when found.

    Args:
        text_chunks: An iterable of text chunks (e.g., from streaming API)

    Yields:
        Expression objects as they are completely parsed from the stream

    Example:
        chunks = ["That's [[a pie", "ce of cake::very", " easy]]!"]
        for expr in stream_expressions(chunks):
            print(f"Found: {expr.phrase}")
    """
    buffer = _StreamingExpressionBuffer()

    for chunk in text_chunks:
        accumulated_text, start_pos = buffer.add_chunk(chunk)

        # Look for complete expressions in accumulated text
        last_complete_pos = 0
        found_any = False

        for match in re.finditer(EXPRESSION_PATTERN, accumulated_text):
            # We only process if this is a complete match (closing ]] found)
            phrase, meaning = match.groups()

            # Normalize and validate
            norm_phrase, norm_meaning = normalize_expression(phrase, meaning)

            if validate_expression(norm_phrase, norm_meaning):
                yield Expression(phrase=norm_phrase, meaning=norm_meaning)
                found_any = True
                last_complete_pos = match.end()

        # Remove processed content from buffer, but keep content after the last
        # complete expression to handle partial expressions
        if found_any:
            buffer.remove_processed(last_complete_pos)

    # After all chunks are processed, check if there's any remaining valid content
    # (though incomplete expressions won't be yielded)
    remaining = buffer.get_remaining()
    if remaining and "[[" in remaining and "::" in remaining and "]]" in remaining:
        # Try to parse any remaining complete expressions
        for match in re.finditer(EXPRESSION_PATTERN, remaining):
            phrase, meaning = match.groups()
            norm_phrase, norm_meaning = normalize_expression(phrase, meaning)

            if validate_expression(norm_phrase, norm_meaning):
                yield Expression(phrase=norm_phrase, meaning=norm_meaning)


# ============================================================================
# Async/Streaming Alternative
# ============================================================================


async def stream_expressions_async(
    text_chunks: Iterable[str],
) -> Generator[Expression, None, None]:
    """Async wrapper for streaming expressions (for future use with async iterables).

    This provides the same functionality as stream_expressions but with
    support for async iterables (AsyncIterable[str]).

    Args:
        text_chunks: An iterable of text chunks

    Yields:
        Expression objects as they are completely parsed from the stream
    """
    # For now, this is a simple wrapper that processes chunks synchronously
    # In future, this can be enhanced to handle actual async iterables
    for expr in stream_expressions(text_chunks):
        yield expr
