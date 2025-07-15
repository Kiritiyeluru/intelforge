#!/usr/bin/env python3
"""
Claude Input-Output Integrity Validator
Specialized validation for Claude/AI-generated content to detect malformed YAML, gibberish, and quality issues.
"""

import re
import json
import yaml
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import string
import math
from pathlib import Path


class IntegrityLevel(Enum):
    """Integrity validation levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IntegrityResult(Enum):
    """Integrity validation results"""
    VALID = "valid"
    INVALID = "invalid"
    SUSPICIOUS = "suspicious"
    CORRUPTED = "corrupted"


@dataclass
class IntegrityCheck:
    """Integrity validation check result"""
    name: str
    level: IntegrityLevel
    result: IntegrityResult
    score: float  # 0.0 to 1.0, higher is better
    message: str
    details: Optional[Dict[str, Any]] = None
    repair_suggestion: Optional[str] = None


class ClaudeIntegrityValidator:
    """
    Validates Claude/AI-generated content for integrity issues:
    - Malformed YAML/JSON
    - Gibberish detection
    - Semantic consistency
    - Format validation
    - Content quality assessment
    """
    
    def __init__(self):
        self.checks: List[IntegrityCheck] = []
        
        # Gibberish detection patterns
        self.gibberish_patterns = [
            r'[a-zA-Z]{20,}',  # Very long words without spaces
            r'[!@#$%^&*()]{5,}',  # Excessive special characters
            r'[A-Z]{10,}',  # Excessive capitals
            r'\b\w*[0-9]+[a-zA-Z]+[0-9]+\w*\b',  # Mixed alphanumeric gibberish
            r'[aeiou]{5,}|[bcdfghjklmnpqrstvwxyz]{5,}',  # Excessive vowels/consonants
        ]
        
        # Common AI hallucination indicators
        self.hallucination_indicators = [
            "as an ai",
            "i cannot",
            "i don't have access",
            "i'm not able to",
            "i apologize",
            "i'm sorry",
            "as a language model",
            "i don't know",
            "placeholder",
            "todo:",
            "fixme:",
            "xxx",
            "lorem ipsum"
        ]
    
    def validate_yaml_content(self, content: str, source: str = "unknown") -> List[IntegrityCheck]:
        """Validate YAML content for syntax and structure"""
        checks = []
        
        try:
            # Basic YAML parsing
            parsed_yaml = yaml.safe_load(content)
            
            if parsed_yaml is None:
                checks.append(IntegrityCheck(
                    name=f"yaml_empty_{source}",
                    level=IntegrityLevel.HIGH,
                    result=IntegrityResult.INVALID,
                    score=0.0,
                    message="YAML content is empty or null",
                    repair_suggestion="Provide valid YAML content"
                ))
            else:
                checks.append(IntegrityCheck(
                    name=f"yaml_syntax_{source}",
                    level=IntegrityLevel.CRITICAL,
                    result=IntegrityResult.VALID,
                    score=1.0,
                    message="YAML syntax is valid"
                ))
                
                # Check for expected structure
                structure_score = self._assess_yaml_structure(parsed_yaml)
                if structure_score < 0.5:
                    checks.append(IntegrityCheck(
                        name=f"yaml_structure_{source}",
                        level=IntegrityLevel.HIGH,
                        result=IntegrityResult.SUSPICIOUS,
                        score=structure_score,
                        message="YAML structure appears incomplete or malformed",
                        details={"structure_score": structure_score}
                    ))
                else:
                    checks.append(IntegrityCheck(
                        name=f"yaml_structure_{source}",
                        level=IntegrityLevel.HIGH,
                        result=IntegrityResult.VALID,
                        score=structure_score,
                        message="YAML structure appears well-formed"
                    ))
                    
        except yaml.YAMLError as e:
            checks.append(IntegrityCheck(
                name=f"yaml_syntax_{source}",
                level=IntegrityLevel.CRITICAL,
                result=IntegrityResult.INVALID,
                score=0.0,
                message=f"YAML syntax error: {e}",
                repair_suggestion="Fix YAML syntax errors before proceeding"
            ))
        except Exception as e:
            checks.append(IntegrityCheck(
                name=f"yaml_error_{source}",
                level=IntegrityLevel.HIGH,
                result=IntegrityResult.CORRUPTED,
                score=0.0,
                message=f"Unexpected error parsing YAML: {e}"
            ))
            
        return checks
    
    def validate_json_content(self, content: str, source: str = "unknown") -> List[IntegrityCheck]:
        """Validate JSON content for syntax and structure"""
        checks = []
        
        try:
            parsed_json = json.loads(content)
            
            checks.append(IntegrityCheck(
                name=f"json_syntax_{source}",
                level=IntegrityLevel.CRITICAL,
                result=IntegrityResult.VALID,
                score=1.0,
                message="JSON syntax is valid"
            ))
            
            # Check for expected structure
            structure_score = self._assess_json_structure(parsed_json)
            if structure_score < 0.5:
                checks.append(IntegrityCheck(
                    name=f"json_structure_{source}",
                    level=IntegrityLevel.HIGH,
                    result=IntegrityResult.SUSPICIOUS,
                    score=structure_score,
                    message="JSON structure appears incomplete or unusual",
                    details={"structure_score": structure_score}
                ))
            else:
                checks.append(IntegrityCheck(
                    name=f"json_structure_{source}",
                    level=IntegrityLevel.HIGH,
                    result=IntegrityResult.VALID,
                    score=structure_score,
                    message="JSON structure appears well-formed"
                ))
                
        except json.JSONDecodeError as e:
            checks.append(IntegrityCheck(
                name=f"json_syntax_{source}",
                level=IntegrityLevel.CRITICAL,
                result=IntegrityResult.INVALID,
                score=0.0,
                message=f"JSON syntax error: {e}",
                repair_suggestion="Fix JSON syntax errors before proceeding"
            ))
        except Exception as e:
            checks.append(IntegrityCheck(
                name=f"json_error_{source}",
                level=IntegrityLevel.HIGH,
                result=IntegrityResult.CORRUPTED,
                score=0.0,
                message=f"Unexpected error parsing JSON: {e}"
            ))
            
        return checks
    
    def validate_text_quality(self, content: str, source: str = "unknown") -> List[IntegrityCheck]:
        """Validate text content quality and detect gibberish"""
        checks = []
        
        if not content or len(content.strip()) == 0:
            checks.append(IntegrityCheck(
                name=f"text_empty_{source}",
                level=IntegrityLevel.HIGH,
                result=IntegrityResult.INVALID,
                score=0.0,
                message="Text content is empty"
            ))
            return checks
        
        # Gibberish detection
        gibberish_score = self._detect_gibberish(content)
        if gibberish_score > 0.7:
            checks.append(IntegrityCheck(
                name=f"text_gibberish_{source}",
                level=IntegrityLevel.HIGH,
                result=IntegrityResult.CORRUPTED,
                score=1.0 - gibberish_score,
                message=f"High gibberish probability detected (score: {gibberish_score:.2f})",
                details={"gibberish_score": gibberish_score},
                repair_suggestion="Regenerate content with better parameters"
            ))
        elif gibberish_score > 0.4:
            checks.append(IntegrityCheck(
                name=f"text_gibberish_{source}",
                level=IntegrityLevel.MEDIUM,
                result=IntegrityResult.SUSPICIOUS,
                score=1.0 - gibberish_score,
                message=f"Moderate gibberish probability detected (score: {gibberish_score:.2f})",
                details={"gibberish_score": gibberish_score}
            ))
        else:
            checks.append(IntegrityCheck(
                name=f"text_gibberish_{source}",
                level=IntegrityLevel.MEDIUM,
                result=IntegrityResult.VALID,
                score=1.0 - gibberish_score,
                message="Text appears coherent and readable"
            ))
        
        # AI hallucination detection
        hallucination_score = self._detect_hallucinations(content)
        if hallucination_score > 0.5:
            checks.append(IntegrityCheck(
                name=f"text_hallucination_{source}",
                level=IntegrityLevel.HIGH,
                result=IntegrityResult.SUSPICIOUS,
                score=1.0 - hallucination_score,
                message=f"Potential AI hallucination indicators found (score: {hallucination_score:.2f})",
                details={"hallucination_score": hallucination_score},
                repair_suggestion="Review content for AI artifacts and regenerate if needed"
            ))
        else:
            checks.append(IntegrityCheck(
                name=f"text_hallucination_{source}",
                level=IntegrityLevel.MEDIUM,
                result=IntegrityResult.VALID,
                score=1.0 - hallucination_score,
                message="No obvious AI hallucination indicators detected"
            ))
        
        # Content length and structure
        length_score = self._assess_content_length(content)
        if length_score < 0.3:
            checks.append(IntegrityCheck(
                name=f"text_length_{source}",
                level=IntegrityLevel.MEDIUM,
                result=IntegrityResult.SUSPICIOUS,
                score=length_score,
                message="Content appears too short or too long for expected output",
                details={"length_score": length_score}
            ))
        else:
            checks.append(IntegrityCheck(
                name=f"text_length_{source}",
                level=IntegrityLevel.LOW,
                result=IntegrityResult.VALID,
                score=length_score,
                message="Content length appears appropriate"
            ))
        
        return checks
    
    def validate_claude_output(self, output: str, expected_format: str = "text", source: str = "claude") -> List[IntegrityCheck]:
        """Comprehensive validation of Claude output"""
        checks = []
        
        # Format-specific validation
        if expected_format.lower() == "yaml":
            checks.extend(self.validate_yaml_content(output, source))
        elif expected_format.lower() == "json":
            checks.extend(self.validate_json_content(output, source))
        
        # Always run text quality validation
        checks.extend(self.validate_text_quality(output, source))
        
        # Encoding validation
        encoding_check = self._validate_encoding(output, source)
        checks.append(encoding_check)
        
        return checks
    
    def _assess_yaml_structure(self, data: Any) -> float:
        """Assess YAML structure quality (0.0 to 1.0)"""
        if data is None:
            return 0.0
        
        score = 0.5  # Base score
        
        if isinstance(data, dict):
            score += 0.3
            # Check for reasonable key structure
            if len(data) > 0:
                score += 0.1
                # Check for non-empty values
                non_empty_values = sum(1 for v in data.values() if v is not None and v != "")
                if non_empty_values > len(data) * 0.5:
                    score += 0.1
        elif isinstance(data, list):
            score += 0.2
            if len(data) > 0:
                score += 0.2
        
        return min(score, 1.0)
    
    def _assess_json_structure(self, data: Any) -> float:
        """Assess JSON structure quality (0.0 to 1.0)"""
        return self._assess_yaml_structure(data)  # Same logic applies
    
    def _detect_gibberish(self, text: str) -> float:
        """Detect gibberish in text (0.0 = clean, 1.0 = gibberish)"""
        if not text:
            return 1.0
        
        gibberish_score = 0.0
        text_lower = text.lower()
        
        # Check for gibberish patterns
        for pattern in self.gibberish_patterns:
            matches = len(re.findall(pattern, text, re.IGNORECASE))
            gibberish_score += min(matches * 0.1, 0.3)
        
        # Character distribution analysis
        char_counts = {}
        for char in text_lower:
            if char.isalpha():
                char_counts[char] = char_counts.get(char, 0) + 1
        
        if char_counts:
            # Calculate entropy
            total_chars = sum(char_counts.values())
            entropy = -sum((count / total_chars) * math.log2(count / total_chars) 
                          for count in char_counts.values())
            
            # Normal English has entropy around 4.1-4.3
            if entropy < 2.0 or entropy > 5.0:
                gibberish_score += 0.3
        
        # Word length distribution
        words = text.split()
        if words:
            avg_word_length = sum(len(word) for word in words) / len(words)
            if avg_word_length > 15 or avg_word_length < 2:
                gibberish_score += 0.2
        
        # Vowel/consonant ratio
        vowels = sum(1 for char in text_lower if char in 'aeiou')
        consonants = sum(1 for char in text_lower if char.isalpha() and char not in 'aeiou')
        
        if consonants > 0:
            vowel_ratio = vowels / (vowels + consonants)
            if vowel_ratio < 0.1 or vowel_ratio > 0.7:
                gibberish_score += 0.2
        
        return min(gibberish_score, 1.0)
    
    def _detect_hallucinations(self, text: str) -> float:
        """Detect AI hallucination indicators (0.0 = clean, 1.0 = many indicators)"""
        if not text:
            return 0.0
        
        text_lower = text.lower()
        indicator_count = 0
        
        for indicator in self.hallucination_indicators:
            if indicator in text_lower:
                indicator_count += 1
        
        # Normalize score
        return min(indicator_count / 5.0, 1.0)
    
    def _assess_content_length(self, text: str) -> float:
        """Assess if content length is appropriate (0.0 = bad, 1.0 = good)"""
        if not text:
            return 0.0
        
        word_count = len(text.split())
        char_count = len(text)
        
        # Very rough heuristics for reasonable content
        if word_count < 3:
            return 0.1  # Too short
        elif word_count > 10000:
            return 0.2  # Probably too long
        elif char_count < 20:
            return 0.3  # Very short
        elif char_count > 50000:
            return 0.4  # Very long
        else:
            return 1.0  # Reasonable length
    
    def _validate_encoding(self, text: str, source: str) -> IntegrityCheck:
        """Validate text encoding and character validity"""
        try:
            # Check for valid UTF-8 encoding
            text.encode('utf-8')
            
            # Check for unusual control characters
            control_chars = sum(1 for char in text if ord(char) < 32 and char not in '\n\r\t')
            
            if control_chars > 0:
                return IntegrityCheck(
                    name=f"encoding_{source}",
                    level=IntegrityLevel.MEDIUM,
                    result=IntegrityResult.SUSPICIOUS,
                    score=0.7,
                    message=f"Found {control_chars} unusual control characters",
                    details={"control_char_count": control_chars}
                )
            else:
                return IntegrityCheck(
                    name=f"encoding_{source}",
                    level=IntegrityLevel.LOW,
                    result=IntegrityResult.VALID,
                    score=1.0,
                    message="Text encoding is valid"
                )
                
        except UnicodeEncodeError as e:
            return IntegrityCheck(
                name=f"encoding_{source}",
                level=IntegrityLevel.HIGH,
                result=IntegrityResult.CORRUPTED,
                score=0.0,
                message=f"Text encoding error: {e}",
                repair_suggestion="Fix character encoding issues"
            )
    
    def validate_file_output(self, file_path: Path, expected_format: str = "auto") -> List[IntegrityCheck]:
        """Validate Claude output from a file"""
        checks = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Auto-detect format if needed
            if expected_format == "auto":
                if file_path.suffix.lower() in ['.yaml', '.yml']:
                    expected_format = "yaml"
                elif file_path.suffix.lower() == '.json':
                    expected_format = "json"
                else:
                    expected_format = "text"
            
            checks.extend(self.validate_claude_output(content, expected_format, str(file_path)))
            
        except FileNotFoundError:
            checks.append(IntegrityCheck(
                name=f"file_missing_{file_path.name}",
                level=IntegrityLevel.CRITICAL,
                result=IntegrityResult.INVALID,
                score=0.0,
                message=f"Output file not found: {file_path}"
            ))
        except Exception as e:
            checks.append(IntegrityCheck(
                name=f"file_error_{file_path.name}",
                level=IntegrityLevel.HIGH,
                result=IntegrityResult.CORRUPTED,
                score=0.0,
                message=f"Error reading output file: {e}"
            ))
        
        return checks
    
    def get_integrity_summary(self, checks: List[IntegrityCheck]) -> Dict[str, Any]:
        """Get summary of integrity validation results"""
        if not checks:
            return {"status": "no_checks", "score": 0.0}
        
        total_score = sum(check.score for check in checks) / len(checks)
        
        results = {
            "valid": sum(1 for c in checks if c.result == IntegrityResult.VALID),
            "invalid": sum(1 for c in checks if c.result == IntegrityResult.INVALID),
            "suspicious": sum(1 for c in checks if c.result == IntegrityResult.SUSPICIOUS),
            "corrupted": sum(1 for c in checks if c.result == IntegrityResult.CORRUPTED)
        }
        
        # Determine overall status
        if results["invalid"] > 0 or results["corrupted"] > 0:
            status = "failed"
        elif results["suspicious"] > 0:
            status = "warning"
        else:
            status = "passed"
        
        return {
            "status": status,
            "score": total_score,
            "total_checks": len(checks),
            "results": results,
            "critical_issues": sum(1 for c in checks 
                                 if c.level == IntegrityLevel.CRITICAL 
                                 and c.result != IntegrityResult.VALID)
        }


def validate_claude_output_cli(content: str, format_type: str = "text") -> bool:
    """
    CLI-friendly validation function.
    Returns True if content passes integrity checks, False otherwise.
    """
    validator = ClaudeIntegrityValidator()
    checks = validator.validate_claude_output(content, format_type)
    summary = validator.get_integrity_summary(checks)
    
    return summary["status"] != "failed"


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Claude Integrity Validator")
    parser.add_argument("input", help="Input file or text to validate")
    parser.add_argument("--format", default="auto", help="Expected format (yaml, json, text, auto)")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    validator = ClaudeIntegrityValidator()
    
    # Determine if input is file or text
    if Path(args.input).exists():
        checks = validator.validate_file_output(Path(args.input), args.format)
    else:
        checks = validator.validate_claude_output(args.input, args.format)
    
    summary = validator.get_integrity_summary(checks)
    
    if args.json:
        output = {
            "summary": summary,
            "checks": [
                {
                    "name": check.name,
                    "level": check.level.value,
                    "result": check.result.value,
                    "score": check.score,
                    "message": check.message,
                    "details": check.details,
                    "repair_suggestion": check.repair_suggestion
                }
                for check in checks
            ]
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"🔍 Claude Integrity Validation Report")
        print(f"=" * 45)
        print(f"Status: {summary['status'].upper()}")
        print(f"Overall Score: {summary['score']:.2f}/1.0")
        print(f"Total Checks: {summary['total_checks']}")
        print(f"✅ Valid: {summary['results']['valid']}")
        print(f"❌ Invalid: {summary['results']['invalid']}")
        print(f"⚠️  Suspicious: {summary['results']['suspicious']}")
        print(f"💥 Corrupted: {summary['results']['corrupted']}")
        
        if args.verbose and checks:
            print(f"\n📋 Detailed Results:")
            for check in checks:
                icon = {
                    IntegrityResult.VALID: "✅",
                    IntegrityResult.INVALID: "❌",
                    IntegrityResult.SUSPICIOUS: "⚠️",
                    IntegrityResult.CORRUPTED: "💥"
                }[check.result]
                
                print(f"{icon} [{check.level.value.upper()}] {check.name} ({check.score:.2f}): {check.message}")
                if check.repair_suggestion and check.result != IntegrityResult.VALID:
                    print(f"   💡 Repair: {check.repair_suggestion}")
        
        # Exit with error if failed
        if summary['status'] == 'failed':
            exit(1)