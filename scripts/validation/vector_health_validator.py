#!/usr/bin/env python3
"""
Vector Store Health Validator
Advanced health monitoring for vector stores including empty embeddings detection,
content validation, and dimensional consistency checks.
"""

import json
import sqlite3
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np


class HealthLevel(Enum):
    """Health check severity levels"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class HealthStatus(Enum):
    """Health check results"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"


@dataclass
class HealthCheck:
    """Vector store health check result"""

    name: str
    level: HealthLevel
    status: HealthStatus
    score: float  # 0.0 to 1.0, higher is better
    message: str
    metrics: Optional[Dict[str, Any]] = None
    recommendation: Optional[str] = None


class VectorHealthValidator:
    """
    Comprehensive vector store health validator that detects:
    - Empty or zero embeddings
    - Dimensional inconsistencies
    - Content corruption
    - Storage fragmentation
    - Performance degradation indicators
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.checks: List[HealthCheck] = []

        # Expected embedding dimensions for different models
        self.expected_dimensions = {
            "sentence-transformers": 384,  # all-MiniLM-L6-v2 default
            "openai": 1536,  # text-embedding-ada-002
            "custom": 768,  # Common transformer size
        }

    def validate_chromadb_health(self) -> List[HealthCheck]:
        """Comprehensive ChromaDB health validation"""
        checks = []
        chroma_path = self.project_root / "chroma_storage"

        if not chroma_path.exists():
            checks.append(
                HealthCheck(
                    name="chromadb_existence",
                    level=HealthLevel.MEDIUM,
                    status=HealthStatus.UNHEALTHY,
                    score=0.0,
                    message="ChromaDB storage directory not found",
                )
            )
            return checks

        # Basic structure check
        db_files = list(chroma_path.rglob("*.sqlite*"))
        if not db_files:
            checks.append(
                HealthCheck(
                    name="chromadb_structure",
                    level=HealthLevel.HIGH,
                    status=HealthStatus.UNHEALTHY,
                    score=0.0,
                    message="No ChromaDB database files found",
                    recommendation="Initialize ChromaDB or check storage configuration",
                )
            )
            return checks

        checks.append(
            HealthCheck(
                name="chromadb_structure",
                level=HealthLevel.MEDIUM,
                status=HealthStatus.HEALTHY,
                score=1.0,
                message=f"Found {len(db_files)} ChromaDB database files",
            )
        )

        # Database content validation
        for db_file in db_files[:3]:  # Check first 3 databases
            db_checks = self._validate_chromadb_content(db_file)
            checks.extend(db_checks)

        # Storage size analysis
        storage_checks = self._analyze_chromadb_storage(chroma_path)
        checks.extend(storage_checks)

        return checks

    def validate_qdrant_health(self) -> List[HealthCheck]:
        """Comprehensive Qdrant health validation"""
        checks = []
        qdrant_path = self.project_root / "qdrant_storage"

        if not qdrant_path.exists():
            checks.append(
                HealthCheck(
                    name="qdrant_existence",
                    level=HealthLevel.LOW,
                    status=HealthStatus.DEGRADED,
                    score=0.5,
                    message="Qdrant storage directory not found (optional component)",
                )
            )
            return checks

        # Collection analysis
        collections = [d for d in qdrant_path.iterdir() if d.is_dir()]
        if not collections:
            checks.append(
                HealthCheck(
                    name="qdrant_collections",
                    level=HealthLevel.MEDIUM,
                    status=HealthStatus.UNHEALTHY,
                    score=0.0,
                    message="No Qdrant collections found",
                )
            )
            return checks

        checks.append(
            HealthCheck(
                name="qdrant_collections",
                level=HealthLevel.MEDIUM,
                status=HealthStatus.HEALTHY,
                score=1.0,
                message=f"Found {len(collections)} Qdrant collections",
            )
        )

        # Collection health validation
        for collection in collections[:5]:  # Check first 5 collections
            collection_checks = self._validate_qdrant_collection(collection)
            checks.extend(collection_checks)

        return checks

    def validate_embeddings_file(self) -> List[HealthCheck]:
        """Validate reference embeddings file health"""
        checks = []
        embeddings_file = self.project_root / "scripts" / "reference_embeddings.json"

        if not embeddings_file.exists():
            checks.append(
                HealthCheck(
                    name="embeddings_file_existence",
                    level=HealthLevel.HIGH,
                    status=HealthStatus.UNHEALTHY,
                    score=0.0,
                    message="Reference embeddings file not found",
                    recommendation="Generate reference embeddings using semantic crawler",
                )
            )
            return checks

        try:
            with open(embeddings_file, "r") as f:
                embeddings_data = json.load(f)

            # Structure validation
            if not isinstance(embeddings_data, dict):
                checks.append(
                    HealthCheck(
                        name="embeddings_structure",
                        level=HealthLevel.HIGH,
                        status=HealthStatus.CRITICAL,
                        score=0.0,
                        message="Invalid embeddings file structure",
                    )
                )
                return checks

            # Content analysis
            content_checks = self._analyze_embeddings_content(embeddings_data)
            checks.extend(content_checks)

            # Dimension consistency
            dimension_checks = self._validate_embedding_dimensions(embeddings_data)
            checks.extend(dimension_checks)

            # Quality metrics
            quality_checks = self._assess_embedding_quality(embeddings_data)
            checks.extend(quality_checks)

        except json.JSONDecodeError as e:
            checks.append(
                HealthCheck(
                    name="embeddings_json_syntax",
                    level=HealthLevel.CRITICAL,
                    status=HealthStatus.CRITICAL,
                    score=0.0,
                    message=f"JSON syntax error in embeddings file: {e}",
                    recommendation="Fix JSON syntax or regenerate embeddings file",
                )
            )
        except Exception as e:
            checks.append(
                HealthCheck(
                    name="embeddings_file_error",
                    level=HealthLevel.HIGH,
                    status=HealthStatus.CRITICAL,
                    score=0.0,
                    message=f"Error reading embeddings file: {e}",
                )
            )

        return checks

    def _validate_chromadb_content(self, db_file: Path) -> List[HealthCheck]:
        """Validate ChromaDB database content"""
        checks = []

        try:
            conn = sqlite3.connect(str(db_file))
            cursor = conn.cursor()

            # Get table information
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()

            if not tables:
                checks.append(
                    HealthCheck(
                        name=f"chromadb_tables_{db_file.name}",
                        level=HealthLevel.HIGH,
                        status=HealthStatus.UNHEALTHY,
                        score=0.0,
                        message=f"No tables found in {db_file.name}",
                    )
                )
                conn.close()
                return checks

            # Check for common ChromaDB tables
            table_names = [table[0] for table in tables]
            expected_tables = ["collections", "embeddings", "documents"]
            found_expected = sum(1 for table in expected_tables if table in table_names)

            if found_expected == 0:
                checks.append(
                    HealthCheck(
                        name=f"chromadb_schema_{db_file.name}",
                        level=HealthLevel.HIGH,
                        status=HealthStatus.DEGRADED,
                        score=0.3,
                        message=f"Unexpected table schema in {db_file.name}",
                    )
                )
            else:
                checks.append(
                    HealthCheck(
                        name=f"chromadb_schema_{db_file.name}",
                        level=HealthLevel.MEDIUM,
                        status=HealthStatus.HEALTHY,
                        score=found_expected / len(expected_tables),
                        message=f"Found {found_expected}/{len(expected_tables)} expected tables",
                    )
                )

            # Check for empty embeddings if embeddings table exists
            if "embeddings" in table_names:
                embedding_checks = self._check_chromadb_embeddings(cursor, db_file.name)
                checks.extend(embedding_checks)

            conn.close()

        except sqlite3.Error as e:
            checks.append(
                HealthCheck(
                    name=f"chromadb_access_{db_file.name}",
                    level=HealthLevel.HIGH,
                    status=HealthStatus.CRITICAL,
                    score=0.0,
                    message=f"Database access error: {e}",
                    recommendation="Check database file integrity",
                )
            )
        except Exception as e:
            checks.append(
                HealthCheck(
                    name=f"chromadb_error_{db_file.name}",
                    level=HealthLevel.MEDIUM,
                    status=HealthStatus.DEGRADED,
                    score=0.0,
                    message=f"Unexpected error checking {db_file.name}: {e}",
                )
            )

        return checks

    def _check_chromadb_embeddings(self, cursor, db_name: str) -> List[HealthCheck]:
        """Check ChromaDB embeddings for empty vectors and consistency"""
        checks = []

        try:
            # Count total embeddings
            cursor.execute("SELECT COUNT(*) FROM embeddings")
            total_count = cursor.fetchone()[0]

            if total_count == 0:
                checks.append(
                    HealthCheck(
                        name=f"chromadb_embedding_count_{db_name}",
                        level=HealthLevel.HIGH,
                        status=HealthStatus.UNHEALTHY,
                        score=0.0,
                        message=f"No embeddings found in {db_name}",
                    )
                )
                return checks

            # Sample embeddings for quality check
            cursor.execute("SELECT embedding FROM embeddings LIMIT 100")
            sample_embeddings = cursor.fetchall()

            if not sample_embeddings:
                checks.append(
                    HealthCheck(
                        name=f"chromadb_embedding_sample_{db_name}",
                        level=HealthLevel.HIGH,
                        status=HealthStatus.UNHEALTHY,
                        score=0.0,
                        message=f"Cannot retrieve embedding samples from {db_name}",
                    )
                )
                return checks

            # Analyze sample embeddings
            empty_count = 0
            dimension_set = set()

            for (embedding_blob,) in sample_embeddings:
                if embedding_blob is None or len(embedding_blob) == 0:
                    empty_count += 1
                    continue

                try:
                    # Try to parse as numpy array or list
                    if isinstance(embedding_blob, bytes):
                        # Might be numpy array or pickled data
                        continue
                    elif isinstance(embedding_blob, str):
                        # Might be JSON
                        embedding = json.loads(embedding_blob)
                        if isinstance(embedding, list):
                            dimension_set.add(len(embedding))
                            # Check for zero vectors
                            if all(x == 0 for x in embedding):
                                empty_count += 1
                except:
                    # Skip malformed embeddings
                    continue

            # Report findings
            empty_percentage = (empty_count / len(sample_embeddings)) * 100

            if empty_percentage > 20:
                checks.append(
                    HealthCheck(
                        name=f"chromadb_empty_embeddings_{db_name}",
                        level=HealthLevel.CRITICAL,
                        status=HealthStatus.CRITICAL,
                        score=1.0 - (empty_percentage / 100),
                        message=f"High percentage of empty/zero embeddings: {empty_percentage:.1f}%",
                        metrics={
                            "empty_percentage": empty_percentage,
                            "total_count": total_count,
                        },
                        recommendation="Regenerate embeddings or check embedding pipeline",
                    )
                )
            elif empty_percentage > 5:
                checks.append(
                    HealthCheck(
                        name=f"chromadb_empty_embeddings_{db_name}",
                        level=HealthLevel.HIGH,
                        status=HealthStatus.DEGRADED,
                        score=1.0 - (empty_percentage / 100),
                        message=f"Moderate percentage of empty/zero embeddings: {empty_percentage:.1f}%",
                        metrics={
                            "empty_percentage": empty_percentage,
                            "total_count": total_count,
                        },
                    )
                )
            else:
                checks.append(
                    HealthCheck(
                        name=f"chromadb_empty_embeddings_{db_name}",
                        level=HealthLevel.MEDIUM,
                        status=HealthStatus.HEALTHY,
                        score=1.0,
                        message=f"Low percentage of empty embeddings: {empty_percentage:.1f}%",
                        metrics={
                            "empty_percentage": empty_percentage,
                            "total_count": total_count,
                        },
                    )
                )

            # Dimension consistency
            if len(dimension_set) > 1:
                checks.append(
                    HealthCheck(
                        name=f"chromadb_dimension_consistency_{db_name}",
                        level=HealthLevel.HIGH,
                        status=HealthStatus.DEGRADED,
                        score=0.5,
                        message=f"Inconsistent embedding dimensions found: {sorted(dimension_set)}",
                        recommendation="Check embedding model consistency",
                    )
                )
            elif len(dimension_set) == 1:
                checks.append(
                    HealthCheck(
                        name=f"chromadb_dimension_consistency_{db_name}",
                        level=HealthLevel.MEDIUM,
                        status=HealthStatus.HEALTHY,
                        score=1.0,
                        message=f"Consistent embedding dimensions: {list(dimension_set)[0]}",
                    )
                )

        except Exception as e:
            checks.append(
                HealthCheck(
                    name=f"chromadb_embedding_analysis_{db_name}",
                    level=HealthLevel.MEDIUM,
                    status=HealthStatus.DEGRADED,
                    score=0.0,
                    message=f"Error analyzing embeddings: {e}",
                )
            )

        return checks

    def _validate_qdrant_collection(self, collection_path: Path) -> List[HealthCheck]:
        """Validate Qdrant collection health"""
        checks = []

        try:
            # Check for collection files
            collection_files = list(collection_path.rglob("*"))
            if not collection_files:
                checks.append(
                    HealthCheck(
                        name=f"qdrant_collection_{collection_path.name}",
                        level=HealthLevel.MEDIUM,
                        status=HealthStatus.UNHEALTHY,
                        score=0.0,
                        message=f"Empty Qdrant collection: {collection_path.name}",
                    )
                )
                return checks

            # Basic file structure validation
            data_files = [
                f
                for f in collection_files
                if f.is_file() and f.suffix in [".bin", ".dat"]
            ]

            if not data_files:
                checks.append(
                    HealthCheck(
                        name=f"qdrant_collection_data_{collection_path.name}",
                        level=HealthLevel.MEDIUM,
                        status=HealthStatus.DEGRADED,
                        score=0.3,
                        message=f"No data files found in collection {collection_path.name}",
                    )
                )
            else:
                total_size = sum(f.stat().st_size for f in data_files)

                if total_size < 1024:  # Less than 1KB
                    checks.append(
                        HealthCheck(
                            name=f"qdrant_collection_size_{collection_path.name}",
                            level=HealthLevel.MEDIUM,
                            status=HealthStatus.DEGRADED,
                            score=0.5,
                            message=f"Very small collection size: {total_size} bytes",
                            metrics={
                                "size_bytes": total_size,
                                "file_count": len(data_files),
                            },
                        )
                    )
                else:
                    checks.append(
                        HealthCheck(
                            name=f"qdrant_collection_size_{collection_path.name}",
                            level=HealthLevel.LOW,
                            status=HealthStatus.HEALTHY,
                            score=1.0,
                            message=f"Collection size: {total_size} bytes ({len(data_files)} files)",
                            metrics={
                                "size_bytes": total_size,
                                "file_count": len(data_files),
                            },
                        )
                    )

        except Exception as e:
            checks.append(
                HealthCheck(
                    name=f"qdrant_collection_error_{collection_path.name}",
                    level=HealthLevel.MEDIUM,
                    status=HealthStatus.DEGRADED,
                    score=0.0,
                    message=f"Error validating collection {collection_path.name}: {e}",
                )
            )

        return checks

    def _analyze_chromadb_storage(self, chroma_path: Path) -> List[HealthCheck]:
        """Analyze ChromaDB storage health and fragmentation"""
        checks = []

        try:
            total_size = sum(
                f.stat().st_size for f in chroma_path.rglob("*") if f.is_file()
            )
            file_count = len(list(chroma_path.rglob("*")))

            if total_size == 0:
                checks.append(
                    HealthCheck(
                        name="chromadb_storage_size",
                        level=HealthLevel.HIGH,
                        status=HealthStatus.UNHEALTHY,
                        score=0.0,
                        message="ChromaDB storage is empty",
                    )
                )
            elif total_size < 1024 * 1024:  # Less than 1MB
                checks.append(
                    HealthCheck(
                        name="chromadb_storage_size",
                        level=HealthLevel.MEDIUM,
                        status=HealthStatus.DEGRADED,
                        score=0.6,
                        message=f"Small ChromaDB storage: {total_size / 1024:.1f} KB",
                        metrics={"size_bytes": total_size, "file_count": file_count},
                    )
                )
            else:
                checks.append(
                    HealthCheck(
                        name="chromadb_storage_size",
                        level=HealthLevel.LOW,
                        status=HealthStatus.HEALTHY,
                        score=1.0,
                        message=f"ChromaDB storage: {total_size / (1024*1024):.1f} MB",
                        metrics={"size_bytes": total_size, "file_count": file_count},
                    )
                )

        except Exception as e:
            checks.append(
                HealthCheck(
                    name="chromadb_storage_analysis",
                    level=HealthLevel.MEDIUM,
                    status=HealthStatus.DEGRADED,
                    score=0.0,
                    message=f"Error analyzing ChromaDB storage: {e}",
                )
            )

        return checks

    def _analyze_embeddings_content(self, embeddings_data: Dict) -> List[HealthCheck]:
        """Analyze reference embeddings content for health issues"""
        checks = []

        if not embeddings_data:
            checks.append(
                HealthCheck(
                    name="embeddings_content_empty",
                    level=HealthLevel.HIGH,
                    status=HealthStatus.UNHEALTHY,
                    score=0.0,
                    message="Reference embeddings data is empty",
                )
            )
            return checks

        total_embeddings = len(embeddings_data)
        empty_embeddings = 0
        zero_embeddings = 0

        for key, embedding in embeddings_data.items():
            if not embedding or embedding is None:
                empty_embeddings += 1
            elif isinstance(embedding, list):
                if all(x == 0 for x in embedding):
                    zero_embeddings += 1

        # Calculate health scores
        empty_percentage = (empty_embeddings / total_embeddings) * 100
        zero_percentage = (zero_embeddings / total_embeddings) * 100
        total_bad_percentage = empty_percentage + zero_percentage

        if total_bad_percentage > 20:
            checks.append(
                HealthCheck(
                    name="embeddings_content_quality",
                    level=HealthLevel.CRITICAL,
                    status=HealthStatus.CRITICAL,
                    score=1.0 - (total_bad_percentage / 100),
                    message=f"High percentage of bad embeddings: {total_bad_percentage:.1f}%",
                    metrics={
                        "total_count": total_embeddings,
                        "empty_count": empty_embeddings,
                        "zero_count": zero_embeddings,
                        "bad_percentage": total_bad_percentage,
                    },
                    recommendation="Regenerate reference embeddings",
                )
            )
        elif total_bad_percentage > 5:
            checks.append(
                HealthCheck(
                    name="embeddings_content_quality",
                    level=HealthLevel.HIGH,
                    status=HealthStatus.DEGRADED,
                    score=1.0 - (total_bad_percentage / 100),
                    message=f"Moderate percentage of bad embeddings: {total_bad_percentage:.1f}%",
                    metrics={
                        "total_count": total_embeddings,
                        "empty_count": empty_embeddings,
                        "zero_count": zero_embeddings,
                        "bad_percentage": total_bad_percentage,
                    },
                )
            )
        else:
            checks.append(
                HealthCheck(
                    name="embeddings_content_quality",
                    level=HealthLevel.MEDIUM,
                    status=HealthStatus.HEALTHY,
                    score=1.0,
                    message=f"Good embedding quality: {total_bad_percentage:.1f}% bad embeddings",
                    metrics={
                        "total_count": total_embeddings,
                        "empty_count": empty_embeddings,
                        "zero_count": zero_embeddings,
                        "bad_percentage": total_bad_percentage,
                    },
                )
            )

        return checks

    def _validate_embedding_dimensions(
        self, embeddings_data: Dict
    ) -> List[HealthCheck]:
        """Validate embedding dimensional consistency"""
        checks = []

        dimensions = set()
        valid_embeddings = 0

        for key, embedding in embeddings_data.items():
            if isinstance(embedding, list) and len(embedding) > 0:
                dimensions.add(len(embedding))
                valid_embeddings += 1

        if not dimensions:
            checks.append(
                HealthCheck(
                    name="embeddings_dimensions",
                    level=HealthLevel.HIGH,
                    status=HealthStatus.UNHEALTHY,
                    score=0.0,
                    message="No valid embeddings found for dimension analysis",
                )
            )
            return checks

        if len(dimensions) > 1:
            checks.append(
                HealthCheck(
                    name="embeddings_dimensions",
                    level=HealthLevel.HIGH,
                    status=HealthStatus.DEGRADED,
                    score=0.5,
                    message=f"Inconsistent embedding dimensions: {sorted(dimensions)}",
                    metrics={
                        "dimensions": list(dimensions),
                        "valid_count": valid_embeddings,
                    },
                    recommendation="Ensure consistent embedding model usage",
                )
            )
        else:
            dimension = list(dimensions)[0]

            # Check against expected dimensions
            is_expected = any(
                dimension == exp_dim for exp_dim in self.expected_dimensions.values()
            )

            if is_expected:
                checks.append(
                    HealthCheck(
                        name="embeddings_dimensions",
                        level=HealthLevel.MEDIUM,
                        status=HealthStatus.HEALTHY,
                        score=1.0,
                        message=f"Consistent embedding dimensions: {dimension} (standard size)",
                        metrics={
                            "dimension": dimension,
                            "valid_count": valid_embeddings,
                        },
                    )
                )
            else:
                checks.append(
                    HealthCheck(
                        name="embeddings_dimensions",
                        level=HealthLevel.MEDIUM,
                        status=HealthStatus.HEALTHY,
                        score=0.8,
                        message=f"Consistent embedding dimensions: {dimension} (custom size)",
                        metrics={
                            "dimension": dimension,
                            "valid_count": valid_embeddings,
                        },
                    )
                )

        return checks

    def _assess_embedding_quality(self, embeddings_data: Dict) -> List[HealthCheck]:
        """Assess overall embedding quality metrics"""
        checks = []

        if not embeddings_data:
            return checks

        # Calculate statistics
        valid_embeddings = []
        for key, embedding in embeddings_data.items():
            if isinstance(embedding, list) and len(embedding) > 0:
                valid_embeddings.append(embedding)

        if not valid_embeddings:
            checks.append(
                HealthCheck(
                    name="embeddings_quality_stats",
                    level=HealthLevel.HIGH,
                    status=HealthStatus.UNHEALTHY,
                    score=0.0,
                    message="No valid embeddings for quality analysis",
                )
            )
            return checks

        # Sample quality metrics
        sample_size = min(len(valid_embeddings), 10)
        sample_embeddings = valid_embeddings[:sample_size]

        # Calculate basic statistics
        try:
            # Convert to numpy for analysis
            embeddings_array = np.array(sample_embeddings)

            # Check for variance (embeddings should have some variance)
            variances = np.var(embeddings_array, axis=1)
            low_variance_count = np.sum(variances < 0.001)

            # Check magnitude (embeddings shouldn't be too small or too large)
            magnitudes = np.linalg.norm(embeddings_array, axis=1)
            avg_magnitude = np.mean(magnitudes)

            quality_score = 1.0
            issues = []

            if low_variance_count > sample_size * 0.5:
                quality_score -= 0.4
                issues.append(
                    f"{low_variance_count}/{sample_size} embeddings have very low variance"
                )

            if avg_magnitude < 0.1:
                quality_score -= 0.3
                issues.append(
                    f"Average embedding magnitude is very low: {avg_magnitude:.4f}"
                )
            elif avg_magnitude > 100:
                quality_score -= 0.2
                issues.append(
                    f"Average embedding magnitude is very high: {avg_magnitude:.2f}"
                )

            if quality_score < 0.5:
                checks.append(
                    HealthCheck(
                        name="embeddings_quality_metrics",
                        level=HealthLevel.HIGH,
                        status=HealthStatus.DEGRADED,
                        score=quality_score,
                        message=f"Embedding quality issues detected: {'; '.join(issues)}",
                        metrics={
                            "sample_size": sample_size,
                            "avg_magnitude": float(avg_magnitude),
                            "low_variance_count": int(low_variance_count),
                        },
                        recommendation="Review embedding generation process",
                    )
                )
            else:
                checks.append(
                    HealthCheck(
                        name="embeddings_quality_metrics",
                        level=HealthLevel.MEDIUM,
                        status=HealthStatus.HEALTHY,
                        score=quality_score,
                        message="Embedding quality metrics appear normal",
                        metrics={
                            "sample_size": sample_size,
                            "avg_magnitude": float(avg_magnitude),
                            "low_variance_count": int(low_variance_count),
                        },
                    )
                )

        except Exception as e:
            checks.append(
                HealthCheck(
                    name="embeddings_quality_analysis",
                    level=HealthLevel.MEDIUM,
                    status=HealthStatus.DEGRADED,
                    score=0.5,
                    message=f"Could not complete quality analysis: {e}",
                )
            )

        return checks

    def get_health_summary(self, checks: List[HealthCheck]) -> Dict[str, Any]:
        """Generate comprehensive health summary"""
        if not checks:
            return {"status": "no_checks", "score": 0.0}

        # Calculate overall score
        total_score = sum(check.score for check in checks) / len(checks)

        # Count by status
        status_counts = {
            "healthy": sum(1 for c in checks if c.status == HealthStatus.HEALTHY),
            "degraded": sum(1 for c in checks if c.status == HealthStatus.DEGRADED),
            "unhealthy": sum(1 for c in checks if c.status == HealthStatus.UNHEALTHY),
            "critical": sum(1 for c in checks if c.status == HealthStatus.CRITICAL),
        }

        # Count by level
        level_counts = {
            "critical": sum(1 for c in checks if c.level == HealthLevel.CRITICAL),
            "high": sum(1 for c in checks if c.level == HealthLevel.HIGH),
            "medium": sum(1 for c in checks if c.level == HealthLevel.MEDIUM),
            "low": sum(1 for c in checks if c.level == HealthLevel.LOW),
        }

        # Determine overall status
        if status_counts["critical"] > 0:
            overall_status = "critical"
        elif status_counts["unhealthy"] > 0:
            overall_status = "unhealthy"
        elif status_counts["degraded"] > 0:
            overall_status = "degraded"
        else:
            overall_status = "healthy"

        return {
            "overall_status": overall_status,
            "overall_score": total_score,
            "total_checks": len(checks),
            "status_counts": status_counts,
            "level_counts": level_counts,
            "critical_issues": [
                {
                    "name": c.name,
                    "message": c.message,
                    "recommendation": c.recommendation,
                }
                for c in checks
                if c.status == HealthStatus.CRITICAL
            ],
        }


def quick_vector_health_check() -> bool:
    """
    Quick health check for CLI integration.
    Returns True if vector stores are healthy, False if critical issues found.
    """
    validator = VectorHealthValidator()

    all_checks = []
    all_checks.extend(validator.validate_chromadb_health())
    all_checks.extend(validator.validate_qdrant_health())
    all_checks.extend(validator.validate_embeddings_file())

    summary = validator.get_health_summary(all_checks)
    return summary["overall_status"] not in ["critical", "unhealthy"]


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Vector Store Health Validator")
    parser.add_argument(
        "--component",
        choices=["all", "chromadb", "qdrant", "embeddings"],
        default="all",
        help="Component to validate",
    )
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    validator = VectorHealthValidator()
    all_checks = []

    if args.component in ["all", "chromadb"]:
        all_checks.extend(validator.validate_chromadb_health())

    if args.component in ["all", "qdrant"]:
        all_checks.extend(validator.validate_qdrant_health())

    if args.component in ["all", "embeddings"]:
        all_checks.extend(validator.validate_embeddings_file())

    summary = validator.get_health_summary(all_checks)

    if args.json:
        output = {
            "summary": summary,
            "checks": [
                {
                    "name": check.name,
                    "level": check.level.value,
                    "status": check.status.value,
                    "score": check.score,
                    "message": check.message,
                    "metrics": check.metrics,
                    "recommendation": check.recommendation,
                }
                for check in all_checks
            ],
        }
        print(json.dumps(output, indent=2))
    else:
        print("🔍 Vector Store Health Report")
        print("=" * 40)
        print(f"Overall Status: {summary['overall_status'].upper()}")
        print(f"Overall Score: {summary['overall_score']:.2f}/1.0")
        print(f"Total Checks: {summary['total_checks']}")
        print(f"✅ Healthy: {summary['status_counts']['healthy']}")
        print(f"⚠️  Degraded: {summary['status_counts']['degraded']}")
        print(f"❌ Unhealthy: {summary['status_counts']['unhealthy']}")
        print(f"💥 Critical: {summary['status_counts']['critical']}")

        if summary["critical_issues"]:
            print("\n🚨 Critical Issues:")
            for issue in summary["critical_issues"]:
                print(f"  • {issue['name']}: {issue['message']}")
                if issue["recommendation"]:
                    print(f"    💡 {issue['recommendation']}")

        if args.verbose and all_checks:
            print("\n📋 Detailed Results:")
            for check in all_checks:
                icon = {
                    HealthStatus.HEALTHY: "✅",
                    HealthStatus.DEGRADED: "⚠️",
                    HealthStatus.UNHEALTHY: "❌",
                    HealthStatus.CRITICAL: "💥",
                }[check.status]

                print(
                    f"{icon} [{check.level.value.upper()}] {check.name} ({check.score:.2f}): {check.message}"
                )
                if check.recommendation and check.status != HealthStatus.HEALTHY:
                    print(f"   💡 {check.recommendation}")

        # Exit with error if critical/unhealthy
        if summary["overall_status"] in ["critical", "unhealthy"]:
            exit(1)
