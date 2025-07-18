#!/usr/bin/env python3
"""
PII Detector for IntelForge using Presidio
Provides lightweight PII detection and sanitization for scraped content
"""

import json
import logging
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

try:
    from presidio_analyzer import AnalyzerEngine
    from presidio_analyzer.nlp_engine import NlpEngineProvider
    from presidio_anonymizer import AnonymizerEngine

    PRESIDIO_AVAILABLE = True
except ImportError:
    PRESIDIO_AVAILABLE = False
    logger.warning("Presidio not available, falling back to basic regex patterns")


class PIIType(Enum):
    """PII types for detection"""

    EMAIL = "email"
    PHONE = "phone"
    SSN = "ssn"
    CREDIT_CARD = "credit_card"
    IP_ADDRESS = "ip_address"
    URL = "url"
    PERSON_NAME = "person_name"
    LOCATION = "location"
    DATE = "date"
    CUSTOM = "custom"


@dataclass
class PIIEntity:
    """Detected PII entity"""

    entity_type: PIIType
    text: str
    start: int
    end: int
    confidence: float
    context: Optional[str] = None


@dataclass
class PIIDetectionResult:
    """PII detection results"""

    original_text: str
    sanitized_text: str
    entities: List[PIIEntity]
    total_entities: int
    has_pii: bool
    risk_score: float


class BasicPIIDetector:
    """Basic regex-based PII detector as fallback"""

    def __init__(self):
        self.patterns = {
            PIIType.EMAIL: re.compile(
                r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
            ),
            PIIType.PHONE: re.compile(
                r"(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})"
            ),
            PIIType.SSN: re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
            PIIType.CREDIT_CARD: re.compile(
                r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b"
            ),
            PIIType.IP_ADDRESS: re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
            PIIType.URL: re.compile(
                r"https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?"
            ),
        }

    def detect(self, text: str) -> List[PIIEntity]:
        """Detect PII using basic regex patterns"""
        entities = []

        for pii_type, pattern in self.patterns.items():
            for match in pattern.finditer(text):
                entity = PIIEntity(
                    entity_type=pii_type,
                    text=match.group(),
                    start=match.start(),
                    end=match.end(),
                    confidence=0.8,  # Basic confidence for regex matches
                    context=text[max(0, match.start() - 20) : match.end() + 20],
                )
                entities.append(entity)

        return entities

    def sanitize(self, text: str, entities: List[PIIEntity]) -> str:
        """Sanitize text by replacing PII with placeholders"""
        sanitized = text

        # Sort entities by start position in reverse order to avoid offset issues
        entities_sorted = sorted(entities, key=lambda x: x.start, reverse=True)

        for entity in entities_sorted:
            placeholder = f"[{entity.entity_type.value.upper()}]"
            sanitized = (
                sanitized[: entity.start] + placeholder + sanitized[entity.end :]
            )

        return sanitized


class PIIDetector:
    """Main PII detector with Presidio integration"""

    def __init__(self, use_presidio: bool = True):
        self.use_presidio = use_presidio and PRESIDIO_AVAILABLE
        self.basic_detector = BasicPIIDetector()

        if self.use_presidio:
            try:
                # Initialize Presidio engines
                self.analyzer = AnalyzerEngine()
                self.anonymizer = AnonymizerEngine()
                logger.info("Presidio PII detector initialized successfully")
            except Exception as e:
                logger.warning(
                    f"Failed to initialize Presidio: {e}, falling back to basic detector"
                )
                self.use_presidio = False
        else:
            logger.info("Using basic regex-based PII detection")

    def detect_pii(self, text: str, language: str = "en") -> PIIDetectionResult:
        """Detect PII in text"""
        if not text or not text.strip():
            return PIIDetectionResult(
                original_text=text,
                sanitized_text=text,
                entities=[],
                total_entities=0,
                has_pii=False,
                risk_score=0.0,
            )

        if self.use_presidio:
            entities = self._detect_presidio(text, language)
        else:
            entities = self.basic_detector.detect(text)

        # Sanitize text
        sanitized_text = self._sanitize_text(text, entities)

        # Calculate risk score
        risk_score = self._calculate_risk_score(entities)

        return PIIDetectionResult(
            original_text=text,
            sanitized_text=sanitized_text,
            entities=entities,
            total_entities=len(entities),
            has_pii=len(entities) > 0,
            risk_score=risk_score,
        )

    def _detect_presidio(self, text: str, language: str) -> List[PIIEntity]:
        """Detect PII using Presidio"""
        try:
            # Analyze text with Presidio
            results = self.analyzer.analyze(
                text=text,
                language=language,
                entities=[
                    "PERSON",
                    "EMAIL_ADDRESS",
                    "PHONE_NUMBER",
                    "CREDIT_CARD",
                    "IP_ADDRESS",
                    "LOCATION",
                    "DATE_TIME",
                    "URL",
                    "US_SSN",
                ],
            )

            entities = []
            for result in results:
                # Map Presidio entity types to our PIIType enum
                entity_type = self._map_presidio_type(result.entity_type)

                entity = PIIEntity(
                    entity_type=entity_type,
                    text=text[result.start : result.end],
                    start=result.start,
                    end=result.end,
                    confidence=result.score,
                    context=text[max(0, result.start - 20) : result.end + 20],
                )
                entities.append(entity)

            return entities

        except Exception as e:
            logger.error(f"Presidio detection failed: {e}")
            # Fall back to basic detection
            return self.basic_detector.detect(text)

    def _map_presidio_type(self, presidio_type: str) -> PIIType:
        """Map Presidio entity types to PIIType enum"""
        mapping = {
            "EMAIL_ADDRESS": PIIType.EMAIL,
            "PHONE_NUMBER": PIIType.PHONE,
            "US_SSN": PIIType.SSN,
            "CREDIT_CARD": PIIType.CREDIT_CARD,
            "IP_ADDRESS": PIIType.IP_ADDRESS,
            "URL": PIIType.URL,
            "PERSON": PIIType.PERSON_NAME,
            "LOCATION": PIIType.LOCATION,
            "DATE_TIME": PIIType.DATE,
        }
        return mapping.get(presidio_type, PIIType.CUSTOM)

    def _sanitize_text(self, text: str, entities: List[PIIEntity]) -> str:
        """Sanitize text by replacing PII with placeholders"""
        if self.use_presidio:
            try:
                # Convert entities to Presidio format
                presidio_entities = []
                for entity in entities:
                    presidio_entities.append(
                        {
                            "entity_type": entity.entity_type.value.upper(),
                            "start": entity.start,
                            "end": entity.end,
                        }
                    )

                # Use Presidio anonymizer
                anonymize_result = self.anonymizer.anonymize(
                    text=text, analyzer_results=presidio_entities
                )
                return anonymize_result.text

            except Exception as e:
                logger.error(f"Presidio anonymization failed: {e}")

        # Fall back to basic sanitization
        return self.basic_detector.sanitize(text, entities)

    def _calculate_risk_score(self, entities: List[PIIEntity]) -> float:
        """Calculate risk score based on detected PII"""
        if not entities:
            return 0.0

        # Risk weights for different PII types
        risk_weights = {
            PIIType.SSN: 10.0,
            PIIType.CREDIT_CARD: 9.0,
            PIIType.PHONE: 6.0,
            PIIType.EMAIL: 5.0,
            PIIType.PERSON_NAME: 7.0,
            PIIType.LOCATION: 4.0,
            PIIType.DATE: 3.0,
            PIIType.IP_ADDRESS: 2.0,
            PIIType.URL: 1.0,
            PIIType.CUSTOM: 5.0,
        }

        total_risk = 0.0
        for entity in entities:
            weight = risk_weights.get(entity.entity_type, 1.0)
            confidence_factor = entity.confidence
            total_risk += weight * confidence_factor

        # Normalize to 0-100 scale
        max_possible_risk = len(entities) * 10.0
        if max_possible_risk > 0:
            return min(100.0, (total_risk / max_possible_risk) * 100)

        return 0.0

    def scan_content(self, content: str, source_url: str = None) -> Dict[str, Any]:
        """Scan content and return comprehensive PII report"""
        result = self.detect_pii(content)

        # Categorize entities by type
        entity_counts = {}
        for entity in result.entities:
            entity_type = entity.entity_type.value
            entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1

        return {
            "source_url": source_url,
            "timestamp": __import__("datetime").datetime.now().isoformat(),
            "has_pii": result.has_pii,
            "total_entities": result.total_entities,
            "risk_score": result.risk_score,
            "entity_counts": entity_counts,
            "entities": [
                {
                    "type": entity.entity_type.value,
                    "text": entity.text,
                    "start": entity.start,
                    "end": entity.end,
                    "confidence": entity.confidence,
                    "context": entity.context,
                }
                for entity in result.entities
            ],
            "sanitized_content": result.sanitized_text,
            "content_length": len(content),
            "sanitized_length": len(result.sanitized_text),
            "detector_type": "presidio" if self.use_presidio else "basic",
        }

    def save_scan_report(self, scan_result: Dict[str, Any], output_path: str):
        """Save PII scan report to file"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w") as f:
            json.dump(scan_result, f, indent=2)

        logger.info(f"PII scan report saved to {output_file}")


def sanitize_for_storage(text: str, detector: PIIDetector = None) -> str:
    """Utility function to sanitize text before storage"""
    if detector is None:
        detector = PIIDetector()

    result = detector.detect_pii(text)
    return result.sanitized_text


def check_content_safety(
    content: str, risk_threshold: float = 50.0
) -> Tuple[bool, float]:
    """Check if content is safe to store based on PII risk"""
    detector = PIIDetector()
    result = detector.detect_pii(content)

    is_safe = result.risk_score < risk_threshold
    return is_safe, result.risk_score


if __name__ == "__main__":
    # Test the PII detector
    detector = PIIDetector()

    # Test content with various PII types
    test_content = """
    Hi there, my name is John Smith and my email is john.smith@example.com.
    You can reach me at (555) 123-4567 or visit my website at https://example.com.
    My SSN is 123-45-6789 and my credit card is 4532-1234-5678-9012.
    I live at 123 Main St, New York, NY 10001.
    """

    print("Testing PII Detection:")
    print("=" * 50)

    scan_result = detector.scan_content(test_content, "test_content")

    print(f"Has PII: {scan_result['has_pii']}")
    print(f"Total entities: {scan_result['total_entities']}")
    print(f"Risk score: {scan_result['risk_score']:.1f}")
    print(f"Entity counts: {scan_result['entity_counts']}")
    print("\nDetected entities:")
    for entity in scan_result["entities"]:
        print(
            f"  - {entity['type']}: {entity['text']} (confidence: {entity['confidence']:.2f})"
        )

    print("\nSanitized content:")
    print(scan_result["sanitized_content"])
