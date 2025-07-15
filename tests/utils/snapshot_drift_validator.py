#!/usr/bin/env python3
"""
Snapshot Drift Validator
Uses sentence-transformers for semantic similarity scoring and provides explainable drift detection
for Claude/AI outputs. Returns measurable drift scores with pass/fail criteria.
"""

import json
import os
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
import logging

# Optional imports for enhanced functionality
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity
    ENHANCED_FEATURES_AVAILABLE = True
except ImportError:
    ENHANCED_FEATURES_AVAILABLE = False
    logging.warning("Enhanced features not available. Install sentence-transformers and scikit-learn for full functionality.")

try:
    import difflib
    DIFF_AVAILABLE = True
except ImportError:
    DIFF_AVAILABLE = False


@dataclass
class DriftScore:
    """Data class for drift detection results"""
    module: str
    drift_score: float
    threshold: float
    verdict: str
    diff_reason: str
    tokens_changed: int
    impact_assessment: str
    timestamp: str
    similarity_score: float = 0.0
    confidence: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


@dataclass
class SnapshotData:
    """Data class for snapshot storage"""
    module: str
    content: str
    embeddings: Optional[List[float]]
    timestamp: str
    metadata: Dict[str, Any]
    content_hash: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


class SnapshotDriftValidator:
    """
    Validates semantic drift in AI outputs using snapshot comparison and semantic similarity
    """
    
    def __init__(self, 
                 config_path: Optional[str] = None,
                 snapshots_dir: Optional[str] = None,
                 model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the drift validator
        
        Args:
            config_path: Path to tolerance_config.json
            snapshots_dir: Directory to store snapshots
            model_name: Sentence transformer model name
        """
        self.project_root = Path(__file__).parent.parent.parent
        
        # Load configuration
        self.config_path = config_path or self.project_root / "tolerance_config.json"
        self.config = self._load_config()
        
        # Set up directories
        self.snapshots_dir = Path(snapshots_dir) if snapshots_dir else self.project_root / "snapshots"
        self.snapshots_dir.mkdir(exist_ok=True)
        
        # Initialize model if available
        self.model = None
        self.model_name = model_name
        self.enhanced_features = ENHANCED_FEATURES_AVAILABLE
        if self.enhanced_features:
            try:
                self.model = SentenceTransformer(model_name)
                logging.info(f"Loaded sentence transformer model: {model_name}")
            except Exception as e:
                logging.warning(f"Failed to load model {model_name}: {e}")
                self.enhanced_features = False
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load tolerance configuration"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Default configuration if file doesn't exist
            return {
                "semantic_drift_thresholds": {
                    "semantic_drift_threshold": 0.02,
                    "high_priority_threshold": 0.01,
                    "critical_threshold": 0.005
                },
                "tolerance_levels": {
                    "default": {
                        "acceptable_variance": 0.02,
                        "warning_threshold": 0.015,
                        "critical_threshold": 0.005
                    }
                }
            }
    
    def _get_content_hash(self, content: str) -> str:
        """Generate hash for content deduplication"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]
    
    def _get_module_threshold(self, module_name: str) -> float:
        """Get drift threshold for specific module"""
        modules_config = self.config.get("modules", {})
        if module_name in modules_config:
            return modules_config[module_name].get("drift_threshold", 0.02)
        
        return self.config.get("semantic_drift_thresholds", {}).get("semantic_drift_threshold", 0.02)
    
    def _compute_embeddings(self, text: str) -> Optional[List[float]]:
        """Compute embeddings for text using sentence transformer"""
        if not self.enhanced_features or self.model is None:
            return None
        
        try:
            embeddings = self.model.encode([text])
            return embeddings[0].tolist()
        except Exception as e:
            self.logger.warning(f"Failed to compute embeddings: {e}")
            return None
    
    def _compute_semantic_similarity(self, 
                                   embeddings1: List[float], 
                                   embeddings2: List[float]) -> float:
        """Compute cosine similarity between embeddings"""
        if not self.enhanced_features:
            return 0.0
        
        try:
            # Convert to numpy arrays and reshape for sklearn
            emb1 = np.array(embeddings1).reshape(1, -1)
            emb2 = np.array(embeddings2).reshape(1, -1)
            
            similarity = cosine_similarity(emb1, emb2)[0][0]
            return float(similarity)
        except Exception as e:
            self.logger.warning(f"Failed to compute similarity: {e}")
            return 0.0
    
    def _compute_text_diff(self, text1: str, text2: str) -> Tuple[str, int]:
        """Compute text differences and count changes"""
        if not DIFF_AVAILABLE:
            return "Text comparison not available", 0
        
        try:
            # Split into words for better granularity
            words1 = text1.split()
            words2 = text2.split()
            
            # Compute sequence matcher
            matcher = difflib.SequenceMatcher(None, words1, words2)
            
            # Count changes
            changes = 0
            diff_reasons = []
            
            for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                if tag != 'equal':
                    changes += abs((i2 - i1) - (j1 - j2))
                    if tag == 'replace':
                        diff_reasons.append(f"replaced {i2-i1} words")
                    elif tag == 'delete':
                        diff_reasons.append(f"deleted {i2-i1} words")
                    elif tag == 'insert':
                        diff_reasons.append(f"inserted {j2-j1} words")
            
            diff_reason = ", ".join(diff_reasons) if diff_reasons else "minor wording differences"
            return diff_reason, changes
            
        except Exception as e:
            self.logger.warning(f"Failed to compute text diff: {e}")
            return "Text comparison error", 0
    
    def _assess_impact(self, drift_score: float, threshold: float, changes: int) -> str:
        """Assess the impact of detected drift"""
        if drift_score <= threshold * 0.5:
            return "negligible"
        elif drift_score <= threshold:
            return "minor"
        elif drift_score <= threshold * 2:
            return "moderate"
        elif drift_score <= threshold * 4:
            return "significant"
        else:
            return "critical"
    
    def save_snapshot(self, 
                     module_name: str, 
                     content: str, 
                     metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Save a snapshot of module output
        
        Args:
            module_name: Name of the module
            content: Output content to snapshot
            metadata: Additional metadata
            
        Returns:
            Snapshot ID
        """
        timestamp = datetime.now().isoformat()
        content_hash = self._get_content_hash(content)
        embeddings = self._compute_embeddings(content)
        
        snapshot = SnapshotData(
            module=module_name,
            content=content,
            embeddings=embeddings,
            timestamp=timestamp,
            metadata=metadata or {},
            content_hash=content_hash
        )
        
        # Create module directory
        module_dir = self.snapshots_dir / module_name
        module_dir.mkdir(exist_ok=True)
        
        # Save snapshot
        snapshot_file = module_dir / f"snapshot_{timestamp.replace(':', '-')}.json"
        with open(snapshot_file, 'w') as f:
            json.dump(snapshot.to_dict(), f, indent=2)
        
        self.logger.info(f"Saved snapshot for {module_name}: {snapshot_file}")
        return content_hash
    
    def load_recent_snapshots(self, 
                            module_name: str, 
                            limit: int = 10) -> List[SnapshotData]:
        """Load recent snapshots for a module"""
        module_dir = self.snapshots_dir / module_name
        if not module_dir.exists():
            return []
        
        # Get all snapshot files
        snapshot_files = list(module_dir.glob("snapshot_*.json"))
        snapshot_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        snapshots = []
        for file_path in snapshot_files[:limit]:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    snapshots.append(SnapshotData(**data))
            except Exception as e:
                self.logger.warning(f"Failed to load snapshot {file_path}: {e}")
        
        return snapshots
    
    def validate_drift(self, 
                      module_name: str, 
                      current_content: str,
                      reference_snapshot: Optional[SnapshotData] = None) -> DriftScore:
        """
        Validate semantic drift for module output
        
        Args:
            module_name: Name of the module
            current_content: Current output content
            reference_snapshot: Reference snapshot to compare against
            
        Returns:
            DriftScore with results
        """
        threshold = self._get_module_threshold(module_name)
        timestamp = datetime.now().isoformat()
        
        # Get reference snapshot if not provided
        if reference_snapshot is None:
            recent_snapshots = self.load_recent_snapshots(module_name, limit=1)
            if not recent_snapshots:
                # No reference available - save current as baseline
                self.save_snapshot(module_name, current_content)
                return DriftScore(
                    module=module_name,
                    drift_score=0.0,
                    threshold=threshold,
                    verdict="✅ BASELINE",
                    diff_reason="No reference snapshot available - saved as baseline",
                    tokens_changed=0,
                    impact_assessment="baseline",
                    timestamp=timestamp,
                    similarity_score=1.0,
                    confidence=1.0
                )
            reference_snapshot = recent_snapshots[0]
        
        # Compute drift score
        drift_score = 0.0
        similarity_score = 0.0
        confidence = 0.5  # Default confidence
        
        if self.enhanced_features and reference_snapshot.embeddings:
            # Compute current embeddings
            current_embeddings = self._compute_embeddings(current_content)
            if current_embeddings:
                similarity_score = self._compute_semantic_similarity(
                    reference_snapshot.embeddings, 
                    current_embeddings
                )
                drift_score = 1.0 - similarity_score
                confidence = 0.9  # High confidence with embeddings
        
        # Fallback to text-based comparison
        if drift_score == 0.0:
            # Simple text-based drift estimation
            diff_reason, changes = self._compute_text_diff(
                reference_snapshot.content, 
                current_content
            )
            total_words = len(reference_snapshot.content.split())
            if total_words > 0:
                drift_score = min(changes / total_words, 1.0)
                confidence = 0.6  # Medium confidence with text diff
        else:
            diff_reason, changes = self._compute_text_diff(
                reference_snapshot.content, 
                current_content
            )
        
        # Determine verdict
        if drift_score <= threshold:
            verdict = "✅ PASS"
        elif drift_score <= threshold * 2:
            verdict = "⚠️ WARNING"
        else:
            verdict = "❌ FAIL"
        
        # Assess impact
        impact = self._assess_impact(drift_score, threshold, changes)
        
        return DriftScore(
            module=module_name,
            drift_score=drift_score,
            threshold=threshold,
            verdict=verdict,
            diff_reason=diff_reason,
            tokens_changed=changes,
            impact_assessment=impact,
            timestamp=timestamp,
            similarity_score=similarity_score,
            confidence=confidence
        )
    
    def generate_drift_report(self, 
                            drift_scores: List[DriftScore],
                            output_format: str = "json") -> str:
        """
        Generate a comprehensive drift report
        
        Args:
            drift_scores: List of drift scores to report
            output_format: Output format ("json" or "markdown")
            
        Returns:
            Report content as string
        """
        if output_format == "json":
            return self._generate_json_report(drift_scores)
        elif output_format == "markdown":
            return self._generate_markdown_report(drift_scores)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
    
    def _generate_json_report(self, drift_scores: List[DriftScore]) -> str:
        """Generate JSON format report"""
        report = {
            "report_timestamp": datetime.now().isoformat(),
            "total_modules_tested": len(drift_scores),
            "overall_status": "PASS",
            "summary": {
                "passed": 0,
                "warnings": 0,
                "failed": 0
            },
            "drift_results": []
        }
        
        for score in drift_scores:
            report["drift_results"].append(score.to_dict())
            
            if "PASS" in score.verdict:
                report["summary"]["passed"] += 1
            elif "WARNING" in score.verdict:
                report["summary"]["warnings"] += 1
            elif "FAIL" in score.verdict:
                report["summary"]["failed"] += 1
                report["overall_status"] = "FAIL"
        
        if report["summary"]["warnings"] > 0 and report["overall_status"] == "PASS":
            report["overall_status"] = "WARNING"
        
        return json.dumps(report, indent=2)
    
    def _generate_markdown_report(self, drift_scores: List[DriftScore]) -> str:
        """Generate Markdown format report"""
        lines = [
            "# Semantic Drift Report",
            f"**Generated**: {datetime.now().isoformat()}",
            f"**Total Modules**: {len(drift_scores)}",
            "",
            "## Summary",
            ""
        ]
        
        passed = sum(1 for s in drift_scores if "PASS" in s.verdict)
        warnings = sum(1 for s in drift_scores if "WARNING" in s.verdict)
        failed = sum(1 for s in drift_scores if "FAIL" in s.verdict)
        
        lines.extend([
            f"- ✅ **Passed**: {passed}",
            f"- ⚠️ **Warnings**: {warnings}",
            f"- ❌ **Failed**: {failed}",
            "",
            "## Detailed Results",
            ""
        ])
        
        for score in drift_scores:
            lines.extend([
                f"### {score.module}",
                f"- **Verdict**: {score.verdict}",
                f"- **Drift Score**: {score.drift_score:.4f} (threshold: {score.threshold:.4f})",
                f"- **Similarity**: {score.similarity_score:.4f}",
                f"- **Changes**: {score.tokens_changed} tokens",
                f"- **Impact**: {score.impact_assessment}",
                f"- **Reason**: {score.diff_reason}",
                f"- **Confidence**: {score.confidence:.2f}",
                ""
            ])
        
        return "\n".join(lines)
    
    def cleanup_old_snapshots(self, days_to_keep: int = 30):
        """Clean up snapshots older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        for module_dir in self.snapshots_dir.iterdir():
            if not module_dir.is_dir():
                continue
                
            for snapshot_file in module_dir.glob("snapshot_*.json"):
                try:
                    file_time = datetime.fromtimestamp(snapshot_file.stat().st_mtime)
                    if file_time < cutoff_date:
                        snapshot_file.unlink()
                        self.logger.info(f"Cleaned up old snapshot: {snapshot_file}")
                except Exception as e:
                    self.logger.warning(f"Failed to clean up {snapshot_file}: {e}")


def main():
    """CLI interface for the snapshot drift validator"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Snapshot Drift Validator")
    parser.add_argument("--module", required=True, help="Module name to validate")
    parser.add_argument("--content", required=True, help="Content to validate")
    parser.add_argument("--config", help="Path to tolerance config file")
    parser.add_argument("--snapshots-dir", help="Directory for snapshots")
    parser.add_argument("--save-snapshot", action="store_true", help="Save current content as snapshot")
    parser.add_argument("--output-format", choices=["json", "markdown"], default="json", help="Output format")
    
    args = parser.parse_args()
    
    # Initialize validator
    validator = SnapshotDriftValidator(
        config_path=args.config,
        snapshots_dir=args.snapshots_dir
    )
    
    if args.save_snapshot:
        # Save snapshot mode
        snapshot_id = validator.save_snapshot(args.module, args.content)
        print(f"Saved snapshot with ID: {snapshot_id}")
    else:
        # Validation mode
        drift_score = validator.validate_drift(args.module, args.content)
        
        if args.output_format == "json":
            print(json.dumps(drift_score.to_dict(), indent=2))
        else:
            report = validator.generate_drift_report([drift_score], "markdown")
            print(report)


if __name__ == "__main__":
    main()