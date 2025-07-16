#!/usr/bin/env python3
"""
Data Integrity Validator for IntelForge
Validates vector store data integrity including embedding count validation,
vector size checks, and dtype validation as required by Phase 5
"""

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import chromadb
import numpy as np
from chromadb.config import Settings

logger = logging.getLogger(__name__)


@dataclass
class IntegrityCheckResult:
    """Result of a data integrity check"""

    check_name: str
    passed: bool
    expected_value: Any
    actual_value: Any
    error_message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class DataIntegrityValidator:
    """Validates data integrity for vector storage operations"""

    def __init__(self, vector_storage_path: str = "./chroma_storage"):
        self.vector_storage_path = vector_storage_path
        self.client = None
        self.collection = None
        self._initialize_storage()

    def _initialize_storage(self):
        """Initialize ChromaDB client and collection"""
        try:
            self.client = chromadb.PersistentClient(
                path=self.vector_storage_path,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=False,  # Prevent accidental resets
                ),
            )

            # Try to get the default collection
            collections = self.client.list_collections()
            if collections:
                self.collection = collections[0]  # Use first available collection
                logger.info(f"Using collection: {self.collection.name}")
            else:
                logger.warning("No collections found in vector storage")

        except Exception as e:
            logger.error(f"Failed to initialize vector storage: {e}")
            self.client = None
            self.collection = None

    def validate_embedding_count(self) -> IntegrityCheckResult:
        """Validate that embedding count matches metadata count"""
        if not self.collection:
            return IntegrityCheckResult(
                check_name="embedding_count_validation",
                passed=False,
                expected_value="accessible collection",
                actual_value="no collection",
                error_message="Vector storage collection not accessible",
            )

        try:
            # Get collection stats
            collection_count = self.collection.count()

            # Get a sample of data to verify structure
            sample_data = self.collection.get(limit=min(100, collection_count))

            # Check if we have data
            if collection_count == 0:
                return IntegrityCheckResult(
                    check_name="embedding_count_validation",
                    passed=True,
                    expected_value=0,
                    actual_value=0,
                    details={"message": "Empty collection - no data to validate"},
                )

            # Verify that all required fields are present
            embeddings_count = len(sample_data.get("embeddings", []))
            metadatas_count = len(sample_data.get("metadatas", []))
            documents_count = len(sample_data.get("documents", []))
            ids_count = len(sample_data.get("ids", []))

            # All counts should match
            expected_count = embeddings_count
            counts_match = (
                embeddings_count == metadatas_count == documents_count == ids_count
            )

            return IntegrityCheckResult(
                check_name="embedding_count_validation",
                passed=counts_match,
                expected_value=expected_count,
                actual_value={
                    "embeddings": embeddings_count,
                    "metadatas": metadatas_count,
                    "documents": documents_count,
                    "ids": ids_count,
                },
                details={
                    "total_collection_count": collection_count,
                    "sample_size": embeddings_count,
                },
            )

        except Exception as e:
            return IntegrityCheckResult(
                check_name="embedding_count_validation",
                passed=False,
                expected_value="valid count comparison",
                actual_value=str(e),
                error_message=f"Error during count validation: {str(e)}",
            )

    def validate_vector_dimensions(
        self, expected_dim: int = 384
    ) -> IntegrityCheckResult:
        """Validate that all embeddings have the expected dimensions"""
        if not self.collection:
            return IntegrityCheckResult(
                check_name="vector_dimension_validation",
                passed=False,
                expected_value=expected_dim,
                actual_value="no collection",
                error_message="Vector storage collection not accessible",
            )

        try:
            # Get sample data to check dimensions
            sample_data = self.collection.get(limit=100, include=["embeddings"])
            embeddings = sample_data.get("embeddings", [])

            if len(embeddings) == 0:
                return IntegrityCheckResult(
                    check_name="vector_dimension_validation",
                    passed=True,
                    expected_value=expected_dim,
                    actual_value=0,
                    details={"message": "No embeddings found - nothing to validate"},
                )

            # Check dimensions for each embedding
            dimension_issues = []
            for i, embedding in enumerate(embeddings):
                if len(embedding) != expected_dim:
                    dimension_issues.append(
                        {"index": i, "expected": expected_dim, "actual": len(embedding)}
                    )

            all_dimensions_correct = len(dimension_issues) == 0

            return IntegrityCheckResult(
                check_name="vector_dimension_validation",
                passed=all_dimensions_correct,
                expected_value=expected_dim,
                actual_value=f"{len(embeddings)} embeddings checked",
                details={
                    "total_embeddings": len(embeddings),
                    "dimension_issues": dimension_issues[:10],  # First 10 issues
                    "total_issues": len(dimension_issues),
                },
            )

        except Exception as e:
            return IntegrityCheckResult(
                check_name="vector_dimension_validation",
                passed=False,
                expected_value=expected_dim,
                actual_value=str(e),
                error_message=f"Error during dimension validation: {str(e)}",
            )

    def validate_vector_dtype(
        self, expected_dtype: str = "float32"
    ) -> IntegrityCheckResult:
        """Validate that all embeddings have the expected data type"""
        if not self.collection:
            return IntegrityCheckResult(
                check_name="vector_dtype_validation",
                passed=False,
                expected_value=expected_dtype,
                actual_value="no collection",
                error_message="Vector storage collection not accessible",
            )

        try:
            # Get sample data to check dtypes
            sample_data = self.collection.get(limit=100, include=["embeddings"])
            embeddings = sample_data.get("embeddings", [])

            if len(embeddings) == 0:
                return IntegrityCheckResult(
                    check_name="vector_dtype_validation",
                    passed=True,
                    expected_value=expected_dtype,
                    actual_value=0,
                    details={"message": "No embeddings found - nothing to validate"},
                )

            # Check data types for each embedding
            dtype_issues = []
            zero_vectors = []

            for i, embedding in enumerate(embeddings):
                # Convert to numpy array to check dtype
                np_embedding = np.array(embedding)

                # Check dtype
                if str(np_embedding.dtype) != expected_dtype:
                    dtype_issues.append(
                        {
                            "index": i,
                            "expected": expected_dtype,
                            "actual": str(np_embedding.dtype),
                        }
                    )

                # Check for zero vectors (all values are 0.0)
                if np.all(np_embedding == 0.0):
                    zero_vectors.append(i)

            all_dtypes_correct = len(dtype_issues) == 0
            no_zero_vectors = len(zero_vectors) == 0

            return IntegrityCheckResult(
                check_name="vector_dtype_validation",
                passed=all_dtypes_correct and no_zero_vectors,
                expected_value=f"{expected_dtype} with non-zero values",
                actual_value=f"{len(embeddings)} embeddings checked",
                details={
                    "total_embeddings": len(embeddings),
                    "dtype_issues": dtype_issues[:10],  # First 10 issues
                    "zero_vectors": zero_vectors[:10],  # First 10 zero vectors
                    "total_dtype_issues": len(dtype_issues),
                    "total_zero_vectors": len(zero_vectors),
                },
            )

        except Exception as e:
            return IntegrityCheckResult(
                check_name="vector_dtype_validation",
                passed=False,
                expected_value=expected_dtype,
                actual_value=str(e),
                error_message=f"Error during dtype validation: {str(e)}",
            )

    def validate_metadata_integrity(self) -> IntegrityCheckResult:
        """Validate metadata integrity and required fields"""
        if not self.collection:
            return IntegrityCheckResult(
                check_name="metadata_integrity_validation",
                passed=False,
                expected_value="accessible collection",
                actual_value="no collection",
                error_message="Vector storage collection not accessible",
            )

        try:
            # Get sample data to check metadata
            sample_data = self.collection.get(limit=100, include=["metadatas"])
            metadatas = sample_data.get("metadatas", [])

            if len(metadatas) == 0:
                return IntegrityCheckResult(
                    check_name="metadata_integrity_validation",
                    passed=True,
                    expected_value="valid metadata",
                    actual_value=0,
                    details={"message": "No metadata found - nothing to validate"},
                )

            # Check metadata integrity
            required_fields = ["url", "title", "content_length", "extracted_at"]
            missing_fields = []
            invalid_metadata = []

            for i, metadata in enumerate(metadatas):
                if not isinstance(metadata, dict):
                    invalid_metadata.append(
                        {
                            "index": i,
                            "type": type(metadata).__name__,
                            "expected": "dict",
                        }
                    )
                    continue

                # Check for required fields
                for field in required_fields:
                    if field not in metadata:
                        missing_fields.append({"index": i, "missing_field": field})

            all_metadata_valid = len(missing_fields) == 0 and len(invalid_metadata) == 0

            return IntegrityCheckResult(
                check_name="metadata_integrity_validation",
                passed=all_metadata_valid,
                expected_value="valid metadata with required fields",
                actual_value=f"{len(metadatas)} metadata records checked",
                details={
                    "total_metadata": len(metadatas),
                    "missing_fields": missing_fields[:10],  # First 10 issues
                    "invalid_metadata": invalid_metadata[:10],  # First 10 issues
                    "total_missing_fields": len(missing_fields),
                    "total_invalid_metadata": len(invalid_metadata),
                },
            )

        except Exception as e:
            return IntegrityCheckResult(
                check_name="metadata_integrity_validation",
                passed=False,
                expected_value="valid metadata",
                actual_value=str(e),
                error_message=f"Error during metadata validation: {str(e)}",
            )

    def run_comprehensive_integrity_check(self) -> Dict[str, IntegrityCheckResult]:
        """Run all integrity checks and return results"""
        logger.info("Starting comprehensive data integrity check...")

        checks = {
            "embedding_count": self.validate_embedding_count(),
            "vector_dimensions": self.validate_vector_dimensions(),
            "vector_dtype": self.validate_vector_dtype(),
            "metadata_integrity": self.validate_metadata_integrity(),
        }

        # Log results
        passed_checks = sum(1 for check in checks.values() if check.passed)
        total_checks = len(checks)

        logger.info(
            f"Integrity check completed: {passed_checks}/{total_checks} checks passed"
        )

        return checks

    def generate_integrity_report(self) -> str:
        """Generate a comprehensive integrity report"""
        checks = self.run_comprehensive_integrity_check()

        report = "# Data Integrity Report\n\n"
        report += f"**Generated**: {Path(__file__).stem} at {np.datetime64('now')}\n"
        report += f"**Vector Storage Path**: {self.vector_storage_path}\n\n"

        # Summary
        passed_checks = sum(1 for check in checks.values() if check.passed)
        total_checks = len(checks)

        report += "## Summary\n"
        report += f"- **Total Checks**: {total_checks}\n"
        report += f"- **Passed**: {passed_checks}\n"
        report += f"- **Failed**: {total_checks - passed_checks}\n"
        report += f"- **Success Rate**: {passed_checks/total_checks*100:.1f}%\n\n"

        # Detailed results
        report += "## Detailed Results\n\n"

        for check_name, result in checks.items():
            status = "✅ PASSED" if result.passed else "❌ FAILED"
            report += f"### {check_name.replace('_', ' ').title()}\n"
            report += f"**Status**: {status}\n"
            report += f"**Expected**: {result.expected_value}\n"
            report += f"**Actual**: {result.actual_value}\n"

            if result.error_message:
                report += f"**Error**: {result.error_message}\n"

            if result.details:
                report += f"**Details**: {json.dumps(result.details, indent=2)}\n"

            report += "\n"

        return report


def main():
    """Main function for running data integrity validation"""
    validator = DataIntegrityValidator()

    # Run comprehensive check
    results = validator.run_comprehensive_integrity_check()

    # Print results
    print("\n" + "=" * 60)
    print("DATA INTEGRITY VALIDATION RESULTS")
    print("=" * 60)

    for check_name, result in results.items():
        status = "✅ PASSED" if result.passed else "❌ FAILED"
        print(f"{check_name.replace('_', ' ').title()}: {status}")

        if not result.passed:
            print(f"  Expected: {result.expected_value}")
            print(f"  Actual: {result.actual_value}")
            if result.error_message:
                print(f"  Error: {result.error_message}")

    print("=" * 60)

    # Generate report
    report = validator.generate_integrity_report()

    # Save report
    report_path = Path("data_integrity_report.md")
    with open(report_path, "w") as f:
        f.write(report)

    print(f"\nDetailed report saved to: {report_path}")


if __name__ == "__main__":
    main()
