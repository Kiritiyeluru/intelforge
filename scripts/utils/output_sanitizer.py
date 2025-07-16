#!/usr/bin/env python3
"""
Output sanitization for IntelForge
Implements regex-based filtering and safe output handling for security
"""

import html
import json
import logging
import re
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Tuple


class OutputSanitizer:
    """
    Comprehensive output sanitization for IntelForge
    Handles text cleaning, security filtering, and safe output formatting
    """

    def __init__(self, strict_mode: bool = False):
        self.strict_mode = strict_mode
        self.logger = logging.getLogger(__name__)

        # Security patterns to remove/replace
        self.security_patterns = [
            # Potential credentials
            (
                r'(?i)(password|passwd|pwd|secret|key|token)\s*[=:]\s*["\']?[a-zA-Z0-9_\-!@#$%^&*()]{8,}["\']?',
                "[REDACTED_CREDENTIAL]",
            ),
            # Email addresses (optional, based on requirements)
            (
                r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
                "[EMAIL_REDACTED]",
            ),
            # IP addresses (if needed)
            (r"\b(?:\d{1,3}\.){3}\d{1,3}\b", "[IP_REDACTED]"),
            # Potential file paths with sensitive info
            (
                r"/(?:home|users)/[a-zA-Z0-9_\-]+(?:/[a-zA-Z0-9_\-./]+)?",
                "[PATH_REDACTED]",
            ),
        ]

        # HTML/Script injection patterns
        self.injection_patterns = [
            r"<script[^>]*>.*?</script>",
            r"<iframe[^>]*>.*?</iframe>",
            r"javascript:",
            r"vbscript:",
            r"onload\s*=",
            r"onerror\s*=",
            r"onclick\s*=",
        ]

        # Character filtering patterns
        self.dangerous_chars = [
            "\x00",  # Null byte
            "\x08",  # Backspace
            "\x0b",  # Vertical tab
            "\x0c",  # Form feed
            "\x0e",  # Shift out
            "\x0f",  # Shift in
        ]

        # Safe character allowlist for strict mode
        self.safe_chars_pattern = re.compile(r"[^\x20-\x7E\x09\x0A\x0D]")

    def sanitize_text(self, text: str, preserve_formatting: bool = True) -> str:
        """
        Sanitize text content with security filtering

        Args:
            text: Input text to sanitize
            preserve_formatting: Whether to preserve basic formatting (newlines, tabs)

        Returns:
            str: Sanitized text
        """
        if not isinstance(text, str):
            text = str(text)

        # Remove dangerous characters
        for char in self.dangerous_chars:
            text = text.replace(char, "")

        # Apply security pattern filtering
        for pattern, replacement in self.security_patterns:
            text = re.sub(
                pattern, replacement, text, flags=re.IGNORECASE | re.MULTILINE
            )

        # Remove HTML/script injection attempts
        for pattern in self.injection_patterns:
            text = re.sub(
                pattern, "[SCRIPT_REMOVED]", text, flags=re.IGNORECASE | re.DOTALL
            )

        # HTML escape to prevent injection
        text = html.escape(text, quote=False)

        # Normalize unicode
        text = unicodedata.normalize("NFKC", text)

        # In strict mode, remove non-printable characters
        if self.strict_mode:
            if preserve_formatting:
                # Keep newlines and tabs
                text = re.sub(r"[^\x20-\x7E\x09\x0A\x0D]", "", text)
            else:
                # Remove all non-printable
                text = re.sub(r"[^\x20-\x7E]", "", text)

        # Limit excessive whitespace
        text = re.sub(r"\n{3,}", "\n\n", text)  # Max 2 consecutive newlines
        text = re.sub(r" {4,}", "   ", text)  # Max 3 consecutive spaces

        return text.strip()

    def sanitize_json_output(self, data: Any, max_depth: int = 10) -> Dict[str, Any]:
        """
        Sanitize JSON output data recursively

        Args:
            data: Data structure to sanitize
            max_depth: Maximum recursion depth

        Returns:
            dict: Sanitized data structure
        """
        if max_depth <= 0:
            return {"error": "Max depth reached - data truncated"}

        if isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                safe_key = self.sanitize_text(str(key), preserve_formatting=False)[:100]
                sanitized[safe_key] = self.sanitize_json_output(value, max_depth - 1)
            return sanitized

        elif isinstance(data, list):
            return [
                self.sanitize_json_output(item, max_depth - 1) for item in data[:1000]
            ]  # Limit list size

        elif isinstance(data, str):
            sanitized = self.sanitize_text(data)
            # Limit string length in JSON
            if len(sanitized) > 10000:
                return sanitized[:10000] + "... [TRUNCATED]"
            return sanitized

        elif isinstance(data, (int, float, bool)):
            return data

        elif data is None:
            return None

        else:
            # Convert unknown types to string and sanitize
            return self.sanitize_text(str(data))[:500] + "... [CONVERTED]"

    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename for safe file operations

        Args:
            filename: Original filename

        Returns:
            str: Safe filename
        """
        # Remove path traversal attempts
        filename = filename.replace("..", "").replace("/", "_").replace("\\", "_")

        # Remove dangerous characters for filenames
        filename = re.sub(r'[<>:"|?*\x00-\x1f]', "_", filename)

        # Limit length
        name, ext = Path(filename).stem, Path(filename).suffix
        if len(name) > 200:
            name = name[:200]

        # Ensure it doesn't start with dot or space
        filename = f"{name}{ext}".lstrip(". ")

        # Fallback if empty
        if not filename or filename == "_":
            filename = "sanitized_output"

        return filename

    def create_safe_output_report(
        self, data: Any, title: str = "IntelForge Output"
    ) -> Dict[str, Any]:
        """
        Create a safe, sanitized output report

        Args:
            data: Raw data to include in report
            title: Report title

        Returns:
            dict: Safe report structure
        """
        safe_title = self.sanitize_text(title, preserve_formatting=False)

        report = {
            "metadata": {
                "title": safe_title,
                "timestamp": "TIMESTAMP_PLACEHOLDER",  # To be filled by caller
                "sanitized": True,
                "version": "1.0",
            },
            "data": self.sanitize_json_output(data),
            "security_notes": [
                "This output has been sanitized for security",
                "Sensitive information may have been redacted",
                "Scripts and HTML have been escaped or removed",
            ],
        }

        return report

    def validate_output_safety(self, text: str) -> Tuple[bool, List[str]]:
        """
        Validate if output is safe for display/export

        Args:
            text: Text to validate

        Returns:
            tuple: (is_safe, list_of_issues)
        """
        issues = []

        # Check for potential credentials
        for pattern, _ in self.security_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                issues.append("Potential credentials detected")
                break

        # Check for script injection
        for pattern in self.injection_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                issues.append("Potential script injection detected")
                break

        # Check for dangerous characters
        for char in self.dangerous_chars:
            if char in text:
                issues.append(f"Dangerous character detected: {repr(char)}")

        # Check for excessive size
        if len(text) > 1000000:  # 1MB limit
            issues.append("Output size exceeds safe limits")

        # Check for excessive repetition (potential DoS)
        if self._has_excessive_repetition(text):
            issues.append("Excessive character repetition detected")

        is_safe = len(issues) == 0
        return is_safe, issues

    def _has_excessive_repetition(self, text: str, threshold: int = 1000) -> bool:
        """Check for excessive character repetition"""
        if len(text) < threshold:
            return False

        # Check for repeated characters
        for i in range(min(len(text) - 1, 10000)):  # Sample first 10K chars
            char = text[i]
            if char == text[i + 1]:
                count = 1
                j = i + 1
                while j < len(text) and text[j] == char and count < threshold:
                    count += 1
                    j += 1
                if count >= threshold:
                    return True

        return False

    def get_sanitization_stats(self, original: str, sanitized: str) -> Dict[str, Any]:
        """
        Get statistics about the sanitization process

        Args:
            original: Original text
            sanitized: Sanitized text

        Returns:
            dict: Sanitization statistics
        """
        return {
            "original_length": len(original),
            "sanitized_length": len(sanitized),
            "reduction_percentage": round(
                (1 - len(sanitized) / max(len(original), 1)) * 100, 2
            ),
            "lines_original": original.count("\n") + 1,
            "lines_sanitized": sanitized.count("\n") + 1,
            "characters_removed": len(original) - len(sanitized),
            "contains_redactions": "[REDACTED" in sanitized
            or "[SCRIPT_REMOVED]" in sanitized,
        }


# Convenience functions
_default_sanitizer = OutputSanitizer()


def sanitize_output(text: str, strict: bool = False) -> str:
    """Convenience function for basic text sanitization"""
    sanitizer = OutputSanitizer(strict_mode=strict)
    return sanitizer.sanitize_text(text)


def sanitize_json(data: Any) -> Dict[str, Any]:
    """Convenience function for JSON sanitization"""
    return _default_sanitizer.sanitize_json_output(data)


def safe_filename(filename: str) -> str:
    """Convenience function for filename sanitization"""
    return _default_sanitizer.sanitize_filename(filename)


def validate_safe_output(text: str) -> Tuple[bool, List[str]]:
    """Convenience function for output validation"""
    return _default_sanitizer.validate_output_safety(text)


# CLI integration helper
def create_sanitized_cli_output(data: Any, format_type: str = "json") -> str:
    """
    Create sanitized output for CLI display

    Args:
        data: Data to output
        format_type: Output format ("json", "text", "yaml")

    Returns:
        str: Safe formatted output
    """
    sanitizer = OutputSanitizer()

    if format_type.lower() == "json":
        sanitized_data = sanitizer.sanitize_json_output(data)
        return json.dumps(sanitized_data, indent=2, ensure_ascii=False)

    elif format_type.lower() == "text":
        return sanitizer.sanitize_text(str(data))

    else:
        # Default to text sanitization
        return sanitizer.sanitize_text(str(data))


# Testing and example usage
if __name__ == "__main__":
    # Example usage
    sanitizer = OutputSanitizer()

    # Test text sanitization
    test_text = """
    This is a test with password=secret123 and <script>alert('xss')</script>
    Also email: user@example.com and path: /home/user/secret.txt
    """

    sanitized = sanitizer.sanitize_text(test_text)
    print("Original:", repr(test_text))
    print("Sanitized:", repr(sanitized))

    # Test safety validation
    is_safe, issues = sanitizer.validate_output_safety(test_text)
    print(f"Is safe: {is_safe}")
    print(f"Issues: {issues}")

    # Test JSON sanitization
    test_data = {
        "user": "john",
        "password": "secret123",
        "data": ["item1", "item2", "<script>alert('xss')</script>"],
        "nested": {"api_key": "abc123def456"},
    }

    sanitized_json = sanitizer.sanitize_json_output(test_data)
    print("\nSanitized JSON:")
    print(json.dumps(sanitized_json, indent=2))
