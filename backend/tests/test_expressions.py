"""Tests for expression extraction and normalization module.

Comprehensive tests for parsing, normalizing, validating, and streaming
expressions from text using [[phrase::meaning]] markup format.
"""

import pytest
from src.core.expressions import (
    parse_expressions,
    stream_expressions,
    normalize_expression,
    validate_expression,
    Expression,
)


# ============================================================================
# Tests for validate_expression
# ============================================================================


class TestValidateExpression:
    """Tests for expression validation."""

    def test_valid_expression(self) -> None:
        """Test that a valid expression passes validation."""
        assert validate_expression("a piece of cake", "something very easy") is True

    def test_valid_simple_expression(self) -> None:
        """Test simple valid expression."""
        assert validate_expression("cat", "animal") is True

    def test_empty_phrase_fails(self) -> None:
        """Test that empty phrase fails validation."""
        assert validate_expression("", "meaning") is False

    def test_empty_meaning_fails(self) -> None:
        """Test that empty meaning fails validation."""
        assert validate_expression("phrase", "") is False

    def test_both_empty_fails(self) -> None:
        """Test that both empty fails validation."""
        assert validate_expression("", "") is False

    def test_phrase_too_long_fails(self) -> None:
        """Test that phrase exceeding max length fails."""
        long_phrase = "a" * 201
        assert validate_expression(long_phrase, "meaning") is False

    def test_meaning_too_long_fails(self) -> None:
        """Test that meaning exceeding max length fails."""
        long_meaning = "a" * 501
        assert validate_expression("phrase", long_meaning) is False

    def test_phrase_at_max_length_passes(self) -> None:
        """Test that phrase at max length passes."""
        phrase = "a" * 200
        assert validate_expression(phrase, "meaning") is True

    def test_meaning_at_max_length_passes(self) -> None:
        """Test that meaning at max length passes."""
        meaning = "a" * 500
        assert validate_expression("phrase", meaning) is True

    def test_phrase_no_alphanumeric_fails(self) -> None:
        """Test that phrase with no alphanumeric characters fails."""
        assert validate_expression("!@#$%", "meaning") is False

    def test_meaning_no_alphanumeric_fails(self) -> None:
        """Test that meaning with no alphanumeric characters fails."""
        assert validate_expression("phrase", "!@#$%") is False

    def test_phrase_with_numbers_passes(self) -> None:
        """Test that phrase with numbers passes."""
        assert validate_expression("item123", "meaning") is True

    def test_meaning_with_numbers_passes(self) -> None:
        """Test that meaning with numbers passes."""
        assert validate_expression("phrase", "definition123") is True

    def test_phrase_with_special_chars_but_alnum_passes(self) -> None:
        """Test phrase with special chars mixed with alphanumeric."""
        assert validate_expression("a-piece-of-cake", "very easy") is True

    def test_meaning_with_special_chars_but_alnum_passes(self) -> None:
        """Test meaning with special chars mixed with alphanumeric."""
        assert validate_expression("phrase", "def: easy") is True


# ============================================================================
# Tests for normalize_expression
# ============================================================================


class TestNormalizeExpression:
    """Tests for expression normalization."""

    def test_normalize_strips_whitespace(self) -> None:
        """Test that normalization strips leading/trailing whitespace."""
        phrase, meaning = normalize_expression("  phrase  ", "  meaning  ")
        assert phrase == "phrase"
        assert meaning == "meaning"

    def test_normalize_multiple_spaces(self) -> None:
        """Test that multiple spaces are normalized to single space."""
        phrase, meaning = normalize_expression("a  piece   of    cake", "very   easy")
        assert phrase == "a piece of cake"
        assert meaning == "very easy"

    def test_normalize_newlines(self) -> None:
        """Test that newlines are converted to spaces."""
        phrase, meaning = normalize_expression("a piece\nof cake", "very\neasy")
        assert phrase == "a piece of cake"
        assert meaning == "very easy"

    def test_normalize_tabs(self) -> None:
        """Test that tabs are converted to spaces."""
        phrase, meaning = normalize_expression("a\tpiece", "very\teasy")
        assert phrase == "a piece"
        assert meaning == "very easy"

    def test_normalize_carriage_returns(self) -> None:
        """Test that carriage returns are converted to spaces."""
        phrase, meaning = normalize_expression("a\rpiece", "very\reasy")
        assert phrase == "a piece"
        assert meaning == "very easy"

    def test_normalize_mixed_whitespace(self) -> None:
        """Test normalization with mixed whitespace types."""
        phrase, meaning = normalize_expression("  a \t piece\n of \r cake  ", "very  \n  easy")
        assert phrase == "a piece of cake"
        assert meaning == "very easy"

    def test_normalize_preserves_content(self) -> None:
        """Test that normalization preserves actual content."""
        phrase, meaning = normalize_expression("a-piece-of-cake", "very easy!")
        assert phrase == "a-piece-of-cake"
        assert meaning == "very easy!"

    def test_normalize_empty_strings(self) -> None:
        """Test normalization of empty strings."""
        phrase, meaning = normalize_expression("", "")
        assert phrase == ""
        assert meaning == ""

    def test_normalize_whitespace_only(self) -> None:
        """Test normalization of whitespace-only strings."""
        phrase, meaning = normalize_expression("   ", "  \t\n  ")
        assert phrase == ""
        assert meaning == ""


# ============================================================================
# Tests for parse_expressions
# ============================================================================


class TestParseExpressions:
    """Tests for parsing complete text."""

    def test_parse_single_expression(self) -> None:
        """Test parsing text with a single expression."""
        text = "That's [[a piece of cake::very easy]]!"
        exprs = parse_expressions(text)
        assert len(exprs) == 1
        assert exprs[0].phrase == "a piece of cake"
        assert exprs[0].meaning == "very easy"

    def test_parse_multiple_expressions(self) -> None:
        """Test parsing text with multiple expressions."""
        text = "[[a piece of cake::very easy]] and [[piece of cake::easy]]"
        exprs = parse_expressions(text)
        assert len(exprs) == 2
        assert exprs[0].phrase == "a piece of cake"
        assert exprs[1].phrase == "piece of cake"

    def test_parse_no_expressions(self) -> None:
        """Test parsing text with no expressions."""
        text = "This is plain text with no expressions"
        exprs = parse_expressions(text)
        assert len(exprs) == 0

    def test_parse_adjacent_expressions(self) -> None:
        """Test parsing adjacent expressions."""
        text = "[[first::meaning1]][[second::meaning2]]"
        exprs = parse_expressions(text)
        assert len(exprs) == 2

    def test_parse_expression_with_spaces(self) -> None:
        """Test parsing expression with internal spaces."""
        text = "[[very long phrase::very long meaning]]"
        exprs = parse_expressions(text)
        assert len(exprs) == 1
        assert exprs[0].phrase == "very long phrase"
        assert exprs[0].meaning == "very long meaning"

    def test_parse_expression_with_punctuation(self) -> None:
        """Test parsing expression with punctuation."""
        text = "[[don't cry over spilled milk::accept loss]]"
        exprs = parse_expressions(text)
        assert len(exprs) == 1
        assert exprs[0].phrase == "don't cry over spilled milk"

    def test_parse_expression_with_hyphens(self) -> None:
        """Test parsing expression with hyphens."""
        text = "[[hit-and-run::something done quickly]]"
        exprs = parse_expressions(text)
        assert len(exprs) == 1
        assert exprs[0].phrase == "hit-and-run"

    def test_parse_invalid_expression_no_meaning(self) -> None:
        """Test that expression without meaning separator is not parsed."""
        text = "[[no meaning here]]"
        exprs = parse_expressions(text)
        assert len(exprs) == 0

    def test_parse_invalid_empty_phrase(self) -> None:
        """Test that expression with empty phrase is not included."""
        text = "[[::meaning]]"
        exprs = parse_expressions(text)
        assert len(exprs) == 0

    def test_parse_invalid_empty_meaning(self) -> None:
        """Test that expression with empty meaning is not included."""
        text = "[[phrase::]]"
        exprs = parse_expressions(text)
        assert len(exprs) == 0

    def test_parse_nested_brackets_not_matched(self) -> None:
        """Test that nested brackets within don't break parsing."""
        text = "[[outer [inner]::meaning]]"
        exprs = parse_expressions(text)
        # This should not match due to the regex pattern
        assert len(exprs) == 0

    def test_parse_expression_with_numbers(self) -> None:
        """Test parsing expression with numbers."""
        text = "[[24/7::all the time]]"
        exprs = parse_expressions(text)
        assert len(exprs) == 1
        assert exprs[0].phrase == "24/7"

    def test_parse_expression_whitespace_normalization(self) -> None:
        """Test that whitespace is normalized in parsed expressions."""
        text = "[[a  piece   of    cake::very    easy]]"
        exprs = parse_expressions(text)
        assert len(exprs) == 1
        assert exprs[0].phrase == "a piece of cake"
        assert exprs[0].meaning == "very easy"

    def test_parse_expressions_returns_expression_objects(self) -> None:
        """Test that parsed results are Expression objects."""
        text = "[[phrase::meaning]]"
        exprs = parse_expressions(text)
        assert all(isinstance(e, Expression) for e in exprs)

    def test_parse_real_world_example(self) -> None:
        """Test parsing a real-world example from the spec."""
        text = "That's [[a piece of cake::very easy]]! It's [[piece of cake::easy]]."
        exprs = parse_expressions(text)
        assert len(exprs) == 2
        assert exprs[0].phrase == "a piece of cake"
        assert exprs[0].meaning == "very easy"
        assert exprs[1].phrase == "piece of cake"
        assert exprs[1].meaning == "easy"


# ============================================================================
# Tests for stream_expressions
# ============================================================================


class TestStreamExpressions:
    """Tests for streaming expression parsing."""

    def test_stream_single_complete_chunk(self) -> None:
        """Test streaming with expression in single chunk."""
        chunks = ["That's [[a piece of cake::very easy]]!"]
        exprs = list(stream_expressions(chunks))
        assert len(exprs) == 1
        assert exprs[0].phrase == "a piece of cake"

    def test_stream_expression_split_across_chunks(self) -> None:
        """Test streaming with expression split across multiple chunks."""
        chunks = ["That's [[a pie", "ce of cake::very", " easy]]!"]
        exprs = list(stream_expressions(chunks))
        assert len(exprs) == 1
        assert exprs[0].phrase == "a piece of cake"
        assert exprs[0].meaning == "very easy"

    def test_stream_multiple_chunks_single_expression(self) -> None:
        """Test streaming multiple chunks with single expression."""
        chunks = ["[[a pie", "ce::", "easy", "]]"]
        exprs = list(stream_expressions(chunks))
        assert len(exprs) == 1
        assert exprs[0].phrase == "a piece"
        assert exprs[0].meaning == "easy"

    def test_stream_expression_split_in_middle_of_word(self) -> None:
        """Test streaming with split in middle of word."""
        chunks = ["[[pie", "ce::easy]]"]
        exprs = list(stream_expressions(chunks))
        assert len(exprs) == 1
        assert exprs[0].phrase == "piece"

    def test_stream_multiple_expressions(self) -> None:
        """Test streaming with multiple complete expressions."""
        chunks = [
            "[[first::mean1]]",
            " and ",
            "[[second::mean2]]",
        ]
        exprs = list(stream_expressions(chunks))
        assert len(exprs) == 2
        assert exprs[0].phrase == "first"
        assert exprs[1].phrase == "second"

    def test_stream_expression_split_at_marker(self) -> None:
        """Test streaming with expression split at special marker."""
        chunks = ["[[expression::", "definition]]"]
        exprs = list(stream_expressions(chunks))
        assert len(exprs) == 1
        assert exprs[0].phrase == "expression"
        assert exprs[0].meaning == "definition"

    def test_stream_expression_split_at_opening_bracket(self) -> None:
        """Test streaming with expression starting across chunks."""
        chunks = ["text [[expr", "ession::def]]"]
        exprs = list(stream_expressions(chunks))
        assert len(exprs) == 1
        assert exprs[0].phrase == "expression"

    def test_stream_no_expressions(self) -> None:
        """Test streaming text with no expressions."""
        chunks = ["This is plain", " text with", " no expressions"]
        exprs = list(stream_expressions(chunks))
        assert len(exprs) == 0

    def test_stream_empty_chunks(self) -> None:
        """Test streaming with empty chunks."""
        chunks = ["[[expr::def]]", "", ""]
        exprs = list(stream_expressions(chunks))
        assert len(exprs) == 1

    def test_stream_incomplete_expression_not_yielded(self) -> None:
        """Test that incomplete expression at end is not yielded."""
        chunks = ["[[incomplete::"]
        exprs = list(stream_expressions(chunks))
        assert len(exprs) == 0

    def test_stream_normalizes_expressions(self) -> None:
        """Test that streamed expressions are normalized."""
        chunks = ["[[a  piece::very    easy]]"]
        exprs = list(stream_expressions(chunks))
        assert len(exprs) == 1
        assert exprs[0].phrase == "a piece"
        assert exprs[0].meaning == "very easy"

    def test_stream_validates_expressions(self) -> None:
        """Test that invalid expressions are filtered out."""
        chunks = ["[[::invalid]]"]
        exprs = list(stream_expressions(chunks))
        assert len(exprs) == 0

    def test_stream_whitespace_split(self) -> None:
        """Test streaming with split at whitespace."""
        chunks = ["[[phrase ", "meaning]]"]
        exprs = list(stream_expressions(chunks))
        assert len(exprs) == 0  # Invalid: no :: separator

    def test_stream_complex_real_world(self) -> None:
        """Test streaming a complex real-world scenario."""
        chunks = [
            "Let me explain: [[a piece", " of cake::very easy]]. ",
            "Also, [[piece of cake::easy]]!",
        ]
        exprs = list(stream_expressions(chunks))
        assert len(exprs) == 2
        assert exprs[0].phrase == "a piece of cake"
        assert exprs[1].phrase == "piece of cake"

    def test_stream_expression_with_special_chars(self) -> None:
        """Test streaming expression with special characters."""
        chunks = ["[[don't-cry::don't worry]]"]
        exprs = list(stream_expressions(chunks))
        assert len(exprs) == 1
        assert exprs[0].phrase == "don't-cry"

    def test_stream_large_single_chunk(self) -> None:
        """Test streaming with large single chunk."""
        text = "[[expr::meaning]]" * 100
        chunks = [text]
        exprs = list(stream_expressions(chunks))
        assert len(exprs) == 100

    def test_stream_chunk_by_character(self) -> None:
        """Test streaming where chunks are single characters."""
        text = "[[ab::cd]]"
        chunks = list(text)  # Each character is a chunk
        exprs = list(stream_expressions(chunks))
        assert len(exprs) == 1
        assert exprs[0].phrase == "ab"
        assert exprs[0].meaning == "cd"

    def test_stream_multiple_expressions_split(self) -> None:
        """Test streaming with multiple expressions where some are split."""
        chunks = [
            "[[first::def1]] [[se",
            "cond::def2]] [[third::def3]]",
        ]
        exprs = list(stream_expressions(chunks))
        assert len(exprs) == 3

    def test_stream_expression_at_chunk_boundary(self) -> None:
        """Test expression exactly at chunk boundary."""
        chunks = ["[[expr::def]]", "[[next::def2]]"]
        exprs = list(stream_expressions(chunks))
        assert len(exprs) == 2

    def test_stream_returns_generator(self) -> None:
        """Test that stream_expressions returns a generator."""
        chunks = ["[[expr::def]]"]
        result = stream_expressions(chunks)
        assert hasattr(result, "__iter__")
        assert hasattr(result, "__next__")

    def test_stream_with_actual_generator_input(self) -> None:
        """Test streaming with generator as input."""

        def chunk_generator():
            yield "[[expr"
            yield "ession::def"
            yield "inition]]"

        exprs = list(stream_expressions(chunk_generator()))
        assert len(exprs) == 1
        assert exprs[0].phrase == "expression"


# ============================================================================
# Integration Tests
# ============================================================================


class TestIntegration:
    """Integration tests combining multiple components."""

    def test_parse_and_stream_produce_same_results(self) -> None:
        """Test that parse and stream produce same results for same input."""
        text = "[[first::def1]] [[second::def2]]"

        # Parse complete text
        parsed = parse_expressions(text)

        # Stream complete text as single chunk
        streamed = list(stream_expressions([text]))

        assert len(parsed) == len(streamed)
        for p, s in zip(parsed, streamed):
            assert p.phrase == s.phrase
            assert p.meaning == s.meaning

    def test_parse_and_stream_chunked_produce_same_results(self) -> None:
        """Test parse and stream with chunks produce same results."""
        text = "[[first::def1]] [[second::def2]]"

        # Parse complete
        parsed = parse_expressions(text)

        # Stream with chunks
        chunks = [text[i : i + 5] for i in range(0, len(text), 5)]
        streamed = list(stream_expressions(chunks))

        assert len(parsed) == len(streamed)
        for p, s in zip(parsed, streamed):
            assert p.phrase == s.phrase
            assert p.meaning == s.meaning

    def test_end_to_end_typical_usage(self) -> None:
        """Test end-to-end typical usage pattern."""
        # Simulate agent response received in chunks (like from streaming API)
        response_chunks = [
            "I found three idioms:\n",
            "[[a piece of cake::something",
            " very easy]],\n[[hit the sack::",
            "go to bed]], and\n[[piece of pi",
            "e::something very good]]. ",
            "Good luck!",
        ]

        expressions = list(stream_expressions(response_chunks))

        assert len(expressions) == 3
        assert expressions[0].phrase == "a piece of cake"
        assert expressions[0].meaning == "something very easy"
        assert expressions[1].phrase == "hit the sack"
        assert expressions[1].meaning == "go to bed"
        assert expressions[2].phrase == "piece of pie"
        assert expressions[2].meaning == "something very good"

    def test_mixed_valid_invalid_expressions(self) -> None:
        """Test parsing mix of valid and invalid expressions."""
        text = (
            "[[valid::meaning]] "
            "[[::invalid]] "
            "[[also valid::good]] "
            "[[no meaning here]] "
            "[[another::fine]]"
        )
        exprs = parse_expressions(text)
        assert len(exprs) == 3
        assert exprs[0].phrase == "valid"
        assert exprs[1].phrase == "also valid"
        assert exprs[2].phrase == "another"
