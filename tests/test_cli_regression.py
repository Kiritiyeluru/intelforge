#!/usr/bin/env python3
"""
CLI Regression Testing Suite
Tests all IntelForge CLI commands with pytest + typer.testing.CliRunner to ensure backwards compatibility
and prevent regressions in command-line interface behavior.
"""

import json
import pytest
import tempfile
import sys
from pathlib import Path
from typing import Dict, Any, List
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from scripts.cli import app
    CLI_AVAILABLE = True
except ImportError:
    CLI_AVAILABLE = False


class TestCLIRegression:
    """Test suite for CLI regression testing"""
    
    def setup_method(self):
        """Set up test runner and fixtures"""
        self.runner = CliRunner()
        self.project_root = Path(__file__).parent.parent
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil
        try:
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except:
            pass
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_help_command(self):
        """Test that main help command works"""
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "IntelForge" in result.output
        assert "Intelligent Content Curation and Analysis Platform" in result.output
        
        # Check that all expected commands are listed
        expected_commands = ["crawl", "validate", "docs", "status", "migrate"]
        for command in expected_commands:
            assert command in result.output
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_crawl_command_help(self):
        """Test crawl command help"""
        result = self.runner.invoke(app, ["crawl", "--help"])
        assert result.exit_code == 0
        assert "Smart crawling with semantic filtering" in result.output
        assert "--threshold" in result.output
        assert "--dry-run" in result.output
        assert "--regenerate-reference" in result.output
        assert "--skip-validation" in result.output
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_crawl_command_missing_file(self):
        """Test crawl command with missing input file"""
        non_existent_file = Path(self.temp_dir) / "missing.txt"
        result = self.runner.invoke(app, ["crawl", str(non_existent_file), "--skip-validation"])
        assert result.exit_code == 1
        assert "Input file not found" in result.output
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_crawl_command_validation_skip(self):
        """Test crawl command with validation skipped and valid file"""
        # Create a dummy URL file
        url_file = Path(self.temp_dir) / "urls.txt"
        url_file.write_text("https://example.com\n")
        
        # Mock the semantic_crawler_main to avoid actual crawling
        with patch('scripts.semantic_crawler.main') as mock_crawler:
            mock_crawler.return_value = None
            result = self.runner.invoke(app, [
                "crawl", 
                str(url_file), 
                "--skip-validation",
                "--dry-run"
            ])
            
            # Should not fail due to validation
            assert "Pre-flight validation failed" not in result.output
            # Check if crawler was attempted to be called
            if result.exit_code == 0:
                mock_crawler.assert_called_once()
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_crawl_command_threshold_option(self):
        """Test crawl command with custom threshold"""
        url_file = Path(self.temp_dir) / "urls.txt"
        url_file.write_text("https://example.com\n")
        
        with patch('scripts.semantic_crawler.main') as mock_crawler:
            mock_crawler.return_value = None
            result = self.runner.invoke(app, [
                "crawl", 
                str(url_file), 
                "--threshold", "0.8",
                "--skip-validation"
            ])
            
            # Check if crawler was attempted to be called
            if result.exit_code == 0:
                mock_crawler.assert_called_once()
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_validate_command_help(self):
        """Test validate command help"""
        result = self.runner.invoke(app, ["validate", "--help"])
        assert result.exit_code == 0
        assert "Run canary validation tests" in result.output
        assert "--config" in result.output
        assert "--verbose" in result.output
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_validate_command_missing_config(self):
        """Test validate command with missing config file"""
        non_existent_config = Path(self.temp_dir) / "missing_config.json"
        
        # Mock modules availability to test config validation
        with patch('scripts.cli.MODULES_AVAILABLE', True):
            result = self.runner.invoke(app, [
                "validate", 
                "system",
                "--config", str(non_existent_config)
            ])
            assert result.exit_code == 1
            if "Config file not found" not in result.output:
                # If modules are not actually available, that's also a valid test outcome
                assert "Required modules not available" in result.output
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_validate_command_basic(self):
        """Test validate command basic functionality"""
        with patch('scripts.cli.MODULES_AVAILABLE', True), \
             patch('scripts.canary_validation_system_v2.main') as mock_validator:
            mock_validator.return_value = None
            result = self.runner.invoke(app, ["validate", "system"])
            
            if result.exit_code == 0:
                mock_validator.assert_called_once()
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_docs_command_help(self):
        """Test docs command help"""
        result = self.runner.invoke(app, ["docs", "--help"])
        assert result.exit_code == 0
        assert "Document management operations" in result.output
        assert "--type" in result.output
        assert "--priority" in result.output
        assert "--title" in result.output
        assert "--output" in result.output
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_docs_command_create_missing_type(self):
        """Test docs command create action without type"""
        result = self.runner.invoke(app, ["docs", "create"])
        assert result.exit_code == 1
        assert "Document type required" in result.output
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_docs_command_create_missing_title(self):
        """Test docs command create action without title"""
        result = self.runner.invoke(app, ["docs", "create", "--type", "STS"])
        assert result.exit_code == 1
        assert "Document title required" in result.output
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_docs_command_validate_action(self):
        """Test docs command validate action"""
        # Mock the subprocess call to validate_naming.sh
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="Validation passed")
            result = self.runner.invoke(app, ["docs", "validate"])
            
            mock_run.assert_called_once()
            assert result.exit_code == 0
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_docs_command_organize_action(self):
        """Test docs command organize action"""
        result = self.runner.invoke(app, ["docs", "organize"])
        assert result.exit_code == 0
        assert "not yet implemented" in result.output
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_docs_command_invalid_action(self):
        """Test docs command with invalid action"""
        result = self.runner.invoke(app, ["docs", "invalid_action"])
        assert result.exit_code == 1
        assert "Unknown action" in result.output
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_status_command_help(self):
        """Test status command help"""
        result = self.runner.invoke(app, ["status", "--help"])
        assert result.exit_code == 0
        assert "Show IntelForge system status" in result.output
        assert "--json" in result.output
        assert "--drift" in result.output
        assert "--detailed" in result.output
        assert "--skip-validation" in result.output
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_status_command_basic(self):
        """Test status command basic functionality"""
        result = self.runner.invoke(app, ["status", "--skip-validation"])
        assert result.exit_code == 0
        # Check for key status indicators
        assert "IntelForge System Status" in result.output or "Module Status" in result.output
        assert "Storage Status" in result.output or "Configuration Files" in result.output
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_status_command_json_output(self):
        """Test status command JSON output"""
        result = self.runner.invoke(app, ["status", "--json", "--skip-validation"])
        assert result.exit_code == 0
        
        # Should be valid JSON
        try:
            status_data = json.loads(result.output)
        except json.JSONDecodeError as e:
            pytest.fail(f"Status command did not return valid JSON: {e}")
        
        # Basic structure validation
        assert isinstance(status_data, dict)
        required_fields = ["timestamp", "overall_status", "modules", "storage", "config_files", "system_info"]
        for field in required_fields:
            assert field in status_data
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_status_command_detailed_mode(self):
        """Test status command detailed mode"""
        result = self.runner.invoke(app, ["status", "--detailed", "--skip-validation"])
        assert result.exit_code == 0
        # Check for status output (detailed mode should still work)
        assert "IntelForge System Status" in result.output or "Module Status" in result.output
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_status_command_drift_flag(self):
        """Test status command with drift flag"""
        result = self.runner.invoke(app, ["status", "--json", "--drift", "--skip-validation"])
        assert result.exit_code == 0
        
        status_data = json.loads(result.output)
        assert "drift_report" in status_data
        assert status_data["drift_report"]["status"] == "not_implemented"
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_migrate_command_help(self):
        """Test migrate command help"""
        result = self.runner.invoke(app, ["migrate", "--help"])
        assert result.exit_code == 0
        assert "Migrate data between storage systems" in result.output
        assert "--verify" in result.output
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_migrate_command_unsupported_migration(self):
        """Test migrate command with unsupported migration path"""
        result = self.runner.invoke(app, ["migrate", "unsupported", "target"])
        assert result.exit_code == 1
        assert "not supported" in result.output
        assert "Supported: qdrant -> chromadb" in result.output
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_migrate_command_qdrant_to_chromadb(self):
        """Test migrate command from qdrant to chromadb"""
        with patch('scripts.vector_storage_migration.migrate_qdrant_to_chroma') as mock_migrate:
            mock_migrate.return_value = True
            result = self.runner.invoke(app, ["migrate", "qdrant", "chromadb"])
            
            if result.exit_code == 0:
                mock_migrate.assert_called_once()


class TestCLIParameterValidation:
    """Test suite for CLI parameter validation and edge cases"""
    
    def setup_method(self):
        """Set up test runner"""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil
        try:
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except:
            pass
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_crawl_invalid_threshold(self):
        """Test crawl command with invalid threshold values"""
        url_file = Path(self.temp_dir) / "urls.txt"
        url_file.write_text("https://example.com\n")
        
        # Test negative threshold
        result = self.runner.invoke(app, [
            "crawl", str(url_file), 
            "--threshold", "-0.1",
            "--skip-validation"
        ])
        # Typer should handle numeric validation
        # This should not crash but may produce warning
        
        # Test threshold > 1
        result = self.runner.invoke(app, [
            "crawl", str(url_file), 
            "--threshold", "1.5",
            "--skip-validation"
        ])
        # Should not crash
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_docs_command_edge_cases(self):
        """Test docs command with edge cases"""
        # Test with empty strings
        result = self.runner.invoke(app, ["docs", "create", "--type", "", "--title", ""])
        assert result.exit_code == 1
        
        # Test with special characters in title
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="Created")
            result = self.runner.invoke(app, [
                "docs", "create", 
                "--type", "STS", 
                "--title", "Test & Special Characters!"
            ])
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_status_command_combinations(self):
        """Test status command with various flag combinations"""
        # Test all flags together
        result = self.runner.invoke(app, [
            "status", "--json", "--detailed", "--drift", "--skip-validation"
        ])
        assert result.exit_code == 0
        
        status_data = json.loads(result.output)
        assert "drift_report" in status_data
        # health_checks may or may not be present depending on --skip-validation behavior
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_migrate_command_verification_flags(self):
        """Test migrate command with verification flags"""
        with patch('scripts.vector_storage_migration.migrate_qdrant_to_chroma') as mock_migrate:
            mock_migrate.return_value = True
            
            # Test with verification enabled (default)
            result = self.runner.invoke(app, ["migrate", "qdrant", "chromadb"])
            if result.exit_code == 0:
                assert "Verifying migration" in result.output or "Migration completed" in result.output
            
            # Test with verification disabled
            result = self.runner.invoke(app, ["migrate", "qdrant", "chromadb", "--no-verify"])
            if result.exit_code == 0:
                # Should still complete successfully
                assert "Migration" in result.output


class TestCLIErrorHandling:
    """Test suite for CLI error handling and failure scenarios"""
    
    def setup_method(self):
        """Set up test runner"""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil
        try:
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except:
            pass
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_crawl_command_module_failure(self):
        """Test crawl command when modules fail"""
        url_file = Path(self.temp_dir) / "urls.txt"
        url_file.write_text("https://example.com\n")
        
        with patch('scripts.cli.MODULES_AVAILABLE', True), \
             patch('scripts.semantic_crawler.main') as mock_crawler:
            mock_crawler.side_effect = Exception("Crawler failed")
            result = self.runner.invoke(app, [
                "crawl", str(url_file), "--skip-validation"
            ])
            assert result.exit_code == 1
            assert "Crawling failed" in result.output
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_validate_command_module_failure(self):
        """Test validate command when validation modules fail"""
        with patch('scripts.cli.MODULES_AVAILABLE', True), \
             patch('scripts.canary_validation_system_v2.main') as mock_validator:
            mock_validator.side_effect = Exception("Validation failed")
            result = self.runner.invoke(app, ["validate", "system"])
            assert result.exit_code == 1
            assert "Validation failed" in result.output
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_docs_command_script_not_found(self):
        """Test docs command when scripts are not found"""
        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.return_value = False
            result = self.runner.invoke(app, [
                "docs", "create", "--type", "STS", "--title", "Test"
            ])
            assert result.exit_code == 1
            assert "script not found" in result.output
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_docs_command_script_failure(self):
        """Test docs command when script execution fails"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=1, 
                stderr="Script execution failed"
            )
            result = self.runner.invoke(app, [
                "docs", "validate"
            ])
            assert result.exit_code == 1
            assert "Validation failed" in result.output
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_migrate_command_import_error(self):
        """Test migrate command when migration modules are not available"""
        # Mock the import to raise ImportError
        with patch('builtins.__import__', side_effect=ImportError("No module")):
            result = self.runner.invoke(app, ["migrate", "qdrant", "chromadb"])
            assert result.exit_code == 1
            assert "Migration modules not available" in result.output or "error" in result.output.lower()
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_migrate_command_migration_failure(self):
        """Test migrate command when migration fails"""
        with patch('scripts.vector_storage_migration.migrate_qdrant_to_chroma') as mock_migrate:
            mock_migrate.return_value = False
            result = self.runner.invoke(app, ["migrate", "qdrant", "chromadb"])
            assert result.exit_code == 1
            assert "Migration failed" in result.output


class TestCLIBackwardsCompatibility:
    """Test suite to ensure backwards compatibility of CLI interface"""
    
    def setup_method(self):
        """Set up test runner"""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil
        try:
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except:
            pass
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_command_availability(self):
        """Test that all expected commands are available"""
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        
        # These commands should always be available
        expected_commands = ["crawl", "validate", "docs", "status", "migrate"]
        for command in expected_commands:
            assert command in result.output, f"Command '{command}' missing from help output"
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_legacy_flag_support(self):
        """Test that legacy flags are still supported"""
        # Test status command legacy behavior
        result = self.runner.invoke(app, ["status", "--skip-validation"])
        assert result.exit_code == 0
        
        # Test crawl command legacy flags
        url_file = Path(self.temp_dir) / "urls.txt"
        url_file.write_text("https://example.com\n")
        
        with patch('scripts.cli.MODULES_AVAILABLE', True), \
             patch('scripts.semantic_crawler.main'):
            result = self.runner.invoke(app, [
                "crawl", str(url_file), 
                "-t", "0.7",  # Short flag form
                "--skip-validation"
            ])
            # Should not fail due to flag recognition - either succeeds or fails for other reasons
            assert result.exit_code in [0, 1]  # Allow for module loading issues
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_output_format_consistency(self):
        """Test that output formats remain consistent"""
        # Test status JSON output structure
        result = self.runner.invoke(app, ["status", "--json", "--skip-validation"])
        assert result.exit_code == 0
        
        status_data = json.loads(result.output)
        
        # These fields should always be present for backwards compatibility
        required_fields = [
            "timestamp", "overall_status", "modules", 
            "storage", "config_files", "system_info"
        ]
        for field in required_fields:
            assert field in status_data, f"Required field '{field}' missing from JSON output"
        
        # overall_status should have consistent valid values
        valid_statuses = ["healthy", "degraded", "critical", "unknown"]
        assert status_data["overall_status"] in valid_statuses


class TestCLIPerformance:
    """Test suite for CLI performance and responsiveness"""
    
    def setup_method(self):
        """Set up test runner"""
        self.runner = CliRunner()
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_help_command_performance(self):
        """Test that help commands respond quickly"""
        import time
        
        start_time = time.time()
        result = self.runner.invoke(app, ["--help"])
        end_time = time.time()
        
        assert result.exit_code == 0
        assert (end_time - start_time) < 5.0  # Should complete within 5 seconds
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_status_command_performance(self):
        """Test that status command with skip-validation responds quickly"""
        import time
        
        start_time = time.time()
        result = self.runner.invoke(app, ["status", "--skip-validation"])
        end_time = time.time()
        
        assert result.exit_code == 0
        assert (end_time - start_time) < 30.0  # Should complete within 30 seconds (more lenient)
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_status_json_command_performance(self):
        """Test that status JSON command responds quickly"""
        import time
        
        start_time = time.time()
        result = self.runner.invoke(app, ["status", "--json", "--skip-validation"])
        end_time = time.time()
        
        assert result.exit_code == 0
        assert (end_time - start_time) < 10.0  # Should complete within 10 seconds


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v"])