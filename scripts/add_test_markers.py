#!/usr/bin/env python3
"""
Add pytest markers to existing test files for selective test execution.
Part of Part 3B System Hardening implementation.
"""

import re
from pathlib import Path
from typing import List, Tuple

# Marker mapping based on test file patterns and content
MARKER_MAPPINGS = {
    "test_health_": ["health", "regression", "critical"],
    "test_cli_": ["cli", "regression", "critical"],
    "test_security_": ["security", "regression", "critical"],
    "test_performance_": ["performance", "slow", "regression"],
    "test_ml_": ["ml", "slow", "regression"],
    "test_embedding_": ["ml", "slow", "regression"],
    "test_academic_": ["integration", "slow", "api"],
    "test_researcher_": ["persona", "integration", "slow"],
    "test_trader_": ["persona", "integration", "slow"],
    "test_developer_": ["persona", "integration", "slow"],
    "test_e2e_": ["integration", "full", "slow"],
    "snapshot_drift_": ["drift", "ml", "regression"],
}

# Method-level markers based on method names
METHOD_MARKERS = {
    "test_quick_": ["quick"],
    "test_basic_": ["quick"],
    "test_simple_": ["quick"],
    "test_full_": ["full", "slow"],
    "test_comprehensive_": ["full", "slow"],
    "test_load_": ["load", "slow"],
    "test_performance_": ["performance", "slow"],
    "test_security_": ["security"],
    "test_integration_": ["integration"],
    "test_regression_": ["regression"],
}


class TestMarkerAdder:
    """Add pytest markers to test files systematically."""

    def __init__(self, test_dir: Path):
        self.test_dir = test_dir
        self.processed_files = []
        self.skipped_files = []

    def get_markers_for_file(self, file_path: Path) -> List[str]:
        """Determine appropriate markers for a test file."""
        filename = file_path.name
        markers = set()

        # Apply file-level markers
        for pattern, file_markers in MARKER_MAPPINGS.items():
            if pattern in filename:
                markers.update(file_markers)

        # Default markers for all test files
        if filename.startswith("test_"):
            markers.add("unit")  # Default to unit unless integration/persona

        # Specific overrides
        if "persona" in str(file_path) or "integration" in str(file_path):
            markers.discard("unit")
            markers.add("integration")

        return sorted(list(markers))

    def get_markers_for_method(self, method_name: str) -> List[str]:
        """Determine appropriate markers for a test method."""
        markers = set()

        for pattern, method_markers in METHOD_MARKERS.items():
            if pattern in method_name:
                markers.update(method_markers)

        return sorted(list(markers))

    def add_markers_to_file(self, file_path: Path) -> bool:
        """Add markers to a specific test file."""
        try:
            content = file_path.read_text()

            # Skip if markers already present
            if "@pytest.mark." in content:
                print(f"⏭️  Skipping {file_path.name} - markers already present")
                self.skipped_files.append(file_path)
                return False

            file_markers = self.get_markers_for_file(file_path)
            if not file_markers:
                print(f"⏭️  Skipping {file_path.name} - no applicable markers")
                self.skipped_files.append(file_path)
                return False

            lines = content.split("\n")
            modified_lines = []

            for i, line in enumerate(lines):
                # Add class-level markers
                if re.match(r"^class Test.*:", line):
                    # Add markers before class definition
                    for marker in file_markers:
                        modified_lines.append(f"@pytest.mark.{marker}")
                    modified_lines.append(line)

                # Add method-level markers
                elif re.match(r"    def test_.*:", line):
                    method_markers = self.get_markers_for_method(line.strip())
                    for marker in method_markers:
                        modified_lines.append(f"    @pytest.mark.{marker}")
                    modified_lines.append(line)

                else:
                    modified_lines.append(line)

            # Write modified content
            modified_content = "\n".join(modified_lines)
            file_path.write_text(modified_content)

            print(f"✅ Added markers to {file_path.name}: {', '.join(file_markers)}")
            self.processed_files.append(file_path)
            return True

        except Exception as e:
            print(f"❌ Error processing {file_path.name}: {e}")
            return False

    def process_all_test_files(self) -> Tuple[int, int]:
        """Process all test files in the directory."""
        test_files = list(self.test_dir.rglob("test_*.py"))
        test_files.extend(list(self.test_dir.rglob("*_test.py")))

        # Remove duplicates and sort
        test_files = sorted(set(test_files))

        print(f"🎯 Processing {len(test_files)} test files...")

        processed_count = 0
        for test_file in test_files:
            if self.add_markers_to_file(test_file):
                processed_count += 1

        return processed_count, len(test_files)

    def generate_report(self):
        """Generate a summary report of marker additions."""
        total_files = len(self.processed_files) + len(self.skipped_files)

        print("\n📊 Test Marker Addition Report")
        print("==============================")
        print(f"Total test files found: {total_files}")
        print(f"Files processed: {len(self.processed_files)}")
        print(f"Files skipped: {len(self.skipped_files)}")
        print(f"Success rate: {len(self.processed_files)/total_files*100:.1f}%")

        if self.processed_files:
            print("\n✅ Processed files:")
            for file_path in self.processed_files:
                markers = self.get_markers_for_file(file_path)
                print(f"   {file_path.name}: {', '.join(markers)}")

        if self.skipped_files:
            print("\n⏭️  Skipped files:")
            for file_path in self.skipped_files:
                print(f"   {file_path.name}")


def main():
    """Main entry point for adding test markers."""
    test_dir = Path(__file__).parent.parent / "tests"

    if not test_dir.exists():
        print(f"❌ Test directory not found: {test_dir}")
        return 1

    marker_adder = TestMarkerAdder(test_dir)
    processed, total = marker_adder.process_all_test_files()
    marker_adder.generate_report()

    print(f"\n🎉 Test marker addition complete: {processed}/{total} files processed")
    return 0


if __name__ == "__main__":
    exit(main())
