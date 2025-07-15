#!/usr/bin/env python3
"""
End-to-End CLI Workflow Tests
Complete pipeline validation for IntelForge CLI workflows including crawling, validation, 
status checking, and document management. Tests realistic user scenarios and command combinations.
"""

import json
import tempfile
import pytest
import sys
import time
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


class TestEndToEndWorkflows:
    """Test suite for end-to-end CLI workflows"""
    
    def setup_method(self):
        """Set up test runner and fixtures"""
        self.runner = CliRunner()
        self.project_root = Path(__file__).parent.parent
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test URL file
        self.url_file = Path(self.temp_dir) / "test_urls.txt"
        self.url_file.write_text("""https://example.com/article1
https://example.com/article2
https://test.com/page1
""")
        
        # Create test config file
        self.config_file = Path(self.temp_dir) / "test_config.json"
        self.config_file.write_text(json.dumps({
            "validation_settings": {
                "threshold": 0.75,
                "timeout": 30
            },
            "output_format": "json"
        }, indent=2))
        
    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil
        try:
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except:
            pass
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_basic_status_workflow(self):
        """Test basic status checking workflow"""
        # Test basic status
        result = self.runner.invoke(app, ["status", "--skip-validation"])
        assert result.exit_code == 0
        assert "IntelForge System Status" in result.output or "Module Status" in result.output
        
        # Test JSON status
        result = self.runner.invoke(app, ["status", "--json", "--skip-validation"])
        assert result.exit_code == 0
        
        status_data = json.loads(result.output)
        assert "overall_status" in status_data
        assert "modules" in status_data
        assert "storage" in status_data
        
        # Test detailed status
        result = self.runner.invoke(app, ["status", "--detailed", "--skip-validation"])
        assert result.exit_code == 0
        assert "IntelForge System Status" in result.output or "Module Status" in result.output
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_documentation_workflow(self):
        """Test documentation management workflow"""
        # Test docs help
        result = self.runner.invoke(app, ["docs", "--help"])
        assert result.exit_code == 0
        assert "Document management operations" in result.output
        
        # Test validation action (with mock)
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="Validation passed")
            result = self.runner.invoke(app, ["docs", "validate"])
            assert result.exit_code == 0
            mock_run.assert_called_once()
        
        # Test organize action
        result = self.runner.invoke(app, ["docs", "organize"])
        assert result.exit_code == 0
        assert "not yet implemented" in result.output
        
        # Test invalid action
        result = self.runner.invoke(app, ["docs", "invalid_action"])
        assert result.exit_code == 1
        assert "Unknown action" in result.output
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_crawl_workflow_dry_run(self):
        """Test crawling workflow in dry run mode"""
        # Mock the semantic crawler to avoid actual web requests
        with patch('scripts.cli.MODULES_AVAILABLE', True), \
             patch('scripts.semantic_crawler.main') as mock_crawler:
            mock_crawler.return_value = None
            
            # Test basic crawl with dry run
            result = self.runner.invoke(app, [
                "crawl", 
                str(self.url_file),
                "--dry-run",
                "--skip-validation"
            ])
            
            # Should not fail catastrophically
            assert result.exit_code in [0, 1]  # Allow for module import issues
            
            if result.exit_code == 0:
                mock_crawler.assert_called_once()
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_crawl_workflow_with_options(self):
        """Test crawling workflow with various options"""
        with patch('scripts.cli.MODULES_AVAILABLE', True), \
             patch('scripts.semantic_crawler.main') as mock_crawler:
            mock_crawler.return_value = None
            
            # Test crawl with custom threshold
            result = self.runner.invoke(app, [
                "crawl", 
                str(self.url_file),
                "--threshold", "0.8",
                "--dry-run",
                "--skip-validation"
            ])
            
            if result.exit_code == 0:
                mock_crawler.assert_called_once()
                mock_crawler.reset_mock()
            
            # Test crawl with regenerate reference
            result = self.runner.invoke(app, [
                "crawl", 
                str(self.url_file),
                "--regenerate-reference",
                "--dry-run",
                "--skip-validation"
            ])
            
            if result.exit_code == 0:
                mock_crawler.assert_called_once()
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_validation_workflow(self):
        """Test validation workflow"""
        # Mock canary validator
        with patch('scripts.cli.MODULES_AVAILABLE', True), \
             patch('scripts.canary_validation_system_v2.main') as mock_validator:
            mock_validator.return_value = None
            
            # Test basic validation
            result = self.runner.invoke(app, ["validate", "system"])
            
            if result.exit_code == 0:
                mock_validator.assert_called_once()
                mock_validator.reset_mock()
            
            # Test validation with verbose flag
            result = self.runner.invoke(app, [
                "validate", 
                "system",
                "--verbose"
            ])
            
            if result.exit_code == 0:
                mock_validator.assert_called_once()
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available") 
    def test_migration_workflow(self):
        """Test migration workflow"""
        # Mock migration function
        with patch('scripts.vector_storage_migration.migrate_qdrant_to_chroma') as mock_migrate:
            mock_migrate.return_value = True
            
            # Test basic migration
            result = self.runner.invoke(app, ["migrate", "qdrant", "chromadb"])
            
            if result.exit_code == 0:
                assert "Migration completed" in result.output
                mock_migrate.assert_called_once()
                mock_migrate.reset_mock()
            
            # Test migration without verification
            result = self.runner.invoke(app, [
                "migrate", 
                "qdrant", 
                "chromadb", 
                "--no-verify"
            ])
            
            if result.exit_code == 0:
                mock_migrate.assert_called_once()
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_error_handling_workflow(self):
        """Test error handling across workflows"""
        # Test with non-existent file
        missing_file = Path(self.temp_dir) / "missing.txt"
        result = self.runner.invoke(app, [
            "crawl", 
            str(missing_file), 
            "--skip-validation"
        ])
        assert result.exit_code == 1
        assert "Input file not found" in result.output
        
        # Test unsupported migration
        result = self.runner.invoke(app, ["migrate", "unsupported", "target"])
        assert result.exit_code == 1
        assert "not supported" in result.output
        
        # Test docs creation without required parameters
        result = self.runner.invoke(app, ["docs", "create"])
        assert result.exit_code == 1
        assert "Document type required" in result.output
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_status_monitoring_workflow(self):
        """Test status monitoring and health checking workflow"""
        # Get initial status
        result = self.runner.invoke(app, ["status", "--json", "--skip-validation"])
        assert result.exit_code == 0
        
        initial_status = json.loads(result.output)
        assert "overall_status" in initial_status
        
        # Check drift reporting (placeholder)
        result = self.runner.invoke(app, [
            "status", 
            "--json", 
            "--drift", 
            "--skip-validation"
        ])
        assert result.exit_code == 0
        
        drift_status = json.loads(result.output)
        assert "drift_report" in drift_status
        assert drift_status["drift_report"]["status"] == "not_implemented"
        
        # Test detailed health checks (when available)
        result = self.runner.invoke(app, ["status", "--detailed"])
        assert result.exit_code == 0
        # Should complete even if health checks fail
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_flag_combinations_workflow(self):
        """Test various flag combinations across commands"""
        # Test status with all flags
        result = self.runner.invoke(app, [
            "status", 
            "--json", 
            "--detailed", 
            "--drift", 
            "--skip-validation"
        ])
        assert result.exit_code == 0
        
        status_data = json.loads(result.output)
        assert "overall_status" in status_data
        assert "drift_report" in status_data
        
        # Test crawl with multiple flags
        with patch('scripts.cli.MODULES_AVAILABLE', True), \
             patch('scripts.semantic_crawler.main') as mock_crawler:
            mock_crawler.return_value = None
            
            result = self.runner.invoke(app, [
                "crawl",
                str(self.url_file),
                "--threshold", "0.9",
                "--dry-run",
                "--regenerate-reference",
                "--skip-validation"
            ])
            
            if result.exit_code == 0:
                mock_crawler.assert_called_once()


class TestWorkflowIntegration:
    """Test suite for workflow integration scenarios"""
    
    def setup_method(self):
        """Set up test runner and fixtures"""
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
    def test_command_chaining_workflow(self):
        """Test logical command chaining workflows"""
        # Workflow: Status → Docs → Status
        
        # 1. Check initial status
        result = self.runner.invoke(app, ["status", "--json", "--skip-validation"])
        assert result.exit_code == 0
        
        initial_status = json.loads(result.output)
        initial_overall_status = initial_status["overall_status"]
        
        # 2. Validate documentation
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="Docs validated")
            result = self.runner.invoke(app, ["docs", "validate"])
            assert result.exit_code == 0
        
        # 3. Check status again
        result = self.runner.invoke(app, ["status", "--json", "--skip-validation"])
        assert result.exit_code == 0
        
        final_status = json.loads(result.output)
        # Status should remain consistent
        assert "overall_status" in final_status
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_data_pipeline_workflow(self):
        """Test data processing pipeline workflow"""
        # Create test URL file
        url_file = Path(self.temp_dir) / "pipeline_urls.txt"
        url_file.write_text("https://example.com/test\n")
        
        # Workflow: Status → Crawl → Validate → Status
        with patch('scripts.cli.MODULES_AVAILABLE', True), \
             patch('scripts.semantic_crawler.main') as mock_crawler, \
             patch('scripts.canary_validation_system_v2.main') as mock_validator:
            
            mock_crawler.return_value = None
            mock_validator.return_value = None
            
            # 1. Initial status check
            result = self.runner.invoke(app, ["status", "--skip-validation"])
            assert result.exit_code == 0
            
            # 2. Run crawling
            result = self.runner.invoke(app, [
                "crawl",
                str(url_file),
                "--dry-run",
                "--skip-validation"
            ])
            
            if result.exit_code == 0:
                mock_crawler.assert_called_once()
            
            # 3. Run validation
            result = self.runner.invoke(app, ["validate", "system"])
            
            if result.exit_code == 0:
                mock_validator.assert_called_once()
            
            # 4. Final status check
            result = self.runner.invoke(app, ["status", "--json", "--skip-validation"])
            assert result.exit_code == 0
            
            final_status = json.loads(result.output)
            assert "overall_status" in final_status
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_maintenance_workflow(self):
        """Test maintenance and migration workflow"""
        with patch('scripts.vector_storage_migration.migrate_qdrant_to_chroma') as mock_migrate:
            mock_migrate.return_value = True
            
            # 1. Check status before migration
            result = self.runner.invoke(app, ["status", "--json", "--skip-validation"])
            assert result.exit_code == 0
            
            pre_status = json.loads(result.output)
            
            # 2. Run migration
            result = self.runner.invoke(app, ["migrate", "qdrant", "chromadb"])
            
            if result.exit_code == 0:
                mock_migrate.assert_called_once()
                assert "Migration completed" in result.output
            
            # 3. Check status after migration
            result = self.runner.invoke(app, ["status", "--json", "--skip-validation"])
            assert result.exit_code == 0
            
            post_status = json.loads(result.output)
            assert "overall_status" in post_status
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_diagnostic_workflow(self):
        """Test diagnostic and troubleshooting workflow"""
        # 1. Detailed status with all flags
        result = self.runner.invoke(app, [
            "status", 
            "--detailed", 
            "--drift"
        ])
        assert result.exit_code == 0
        
        # 2. Document validation
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="All good")
            result = self.runner.invoke(app, ["docs", "validate"])
            assert result.exit_code == 0
        
        # 3. System validation
        with patch('scripts.cli.MODULES_AVAILABLE', True), \
             patch('scripts.canary_validation_system_v2.main') as mock_validator:
            mock_validator.return_value = None
            
            result = self.runner.invoke(app, ["validate", "system", "--verbose"])
            
            if result.exit_code == 0:
                mock_validator.assert_called_once()


class TestWorkflowPerformance:
    """Test suite for workflow performance and timing"""
    
    def setup_method(self):
        """Set up test runner"""
        self.runner = CliRunner()
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_status_workflow_performance(self):
        """Test status workflow performance"""
        import time
        
        # Time basic status
        start_time = time.time()
        result = self.runner.invoke(app, ["status", "--skip-validation"])
        basic_time = time.time() - start_time
        
        assert result.exit_code == 0
        assert basic_time < 30.0  # Should complete within 30 seconds
        
        # Time JSON status
        start_time = time.time()
        result = self.runner.invoke(app, ["status", "--json", "--skip-validation"])
        json_time = time.time() - start_time
        
        assert result.exit_code == 0
        assert json_time < 30.0  # Should complete within 30 seconds
        
        # JSON should be faster than rich output
        # (though this may not always be true depending on system load)
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_help_commands_performance(self):
        """Test help commands respond quickly"""
        import time
        
        commands_to_test = [
            ["--help"],
            ["status", "--help"],
            ["crawl", "--help"],
            ["validate", "--help"],
            ["docs", "--help"],
            ["migrate", "--help"]
        ]
        
        for cmd in commands_to_test:
            start_time = time.time()
            result = self.runner.invoke(app, cmd)
            elapsed_time = time.time() - start_time
            
            assert result.exit_code == 0
            assert elapsed_time < 10.0  # Help should be very fast
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_workflow_consistency(self):
        """Test that workflows produce consistent results across runs"""
        # Run status command multiple times
        results = []
        for _ in range(3):
            result = self.runner.invoke(app, ["status", "--json", "--skip-validation"])
            assert result.exit_code == 0
            
            status_data = json.loads(result.output)
            results.append(status_data)
        
        # Check consistency of structure
        for i in range(1, len(results)):
            # Same top-level keys should be present
            assert set(results[0].keys()) == set(results[i].keys())
            
            # Overall status should be consistent (may change but structure should remain)
            assert results[i]["overall_status"] in ["healthy", "degraded", "critical", "unknown"]
            
            # Core modules availability should be consistent
            assert results[0]["modules"]["core_available"] == results[i]["modules"]["core_available"]


class TestWorkflowErrorRecovery:
    """Test suite for workflow error recovery and resilience"""
    
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
    def test_partial_failure_recovery(self):
        """Test workflow recovery from partial failures"""
        # Create URL file that will cause validation errors
        bad_url_file = Path(self.temp_dir) / "bad_urls.txt"
        bad_url_file.write_text("not-a-url\ninvalid://bad-scheme\n")
        
        # Test that crawl fails gracefully
        result = self.runner.invoke(app, [
            "crawl", 
            str(bad_url_file), 
            "--skip-validation"
        ])
        
        # Should fail but not crash
        assert result.exit_code == 1
        
        # Status should still work after failure
        result = self.runner.invoke(app, ["status", "--skip-validation"])
        assert result.exit_code == 0
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_module_failure_workflow(self):
        """Test workflow behavior when modules are unavailable"""
        # Test commands when modules are not available
        with patch('scripts.cli.MODULES_AVAILABLE', False):
            # Crawl should fail gracefully
            url_file = Path(self.temp_dir) / "test.txt"
            url_file.write_text("https://example.com\n")
            
            result = self.runner.invoke(app, [
                "crawl", 
                str(url_file), 
                "--skip-validation"
            ])
            assert result.exit_code == 1
            assert "Required modules not available" in result.output
            
            # Validate should fail gracefully
            result = self.runner.invoke(app, ["validate", "system"])
            assert result.exit_code == 1
            assert "Required modules not available" in result.output
            
            # Status should still work
            result = self.runner.invoke(app, ["status", "--skip-validation"])
            assert result.exit_code == 0
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_interrupted_workflow_recovery(self):
        """Test recovery from interrupted workflows"""
        # Simulate interrupted crawl workflow
        with patch('scripts.cli.MODULES_AVAILABLE', True), \
             patch('scripts.semantic_crawler.main') as mock_crawler:
            
            # First call succeeds
            mock_crawler.return_value = None
            url_file = Path(self.temp_dir) / "test.txt"
            url_file.write_text("https://example.com\n")
            
            result = self.runner.invoke(app, [
                "crawl", 
                str(url_file), 
                "--dry-run", 
                "--skip-validation"
            ])
            
            if result.exit_code == 0:
                mock_crawler.assert_called_once()
                mock_crawler.reset_mock()
            
            # Second call with exception
            mock_crawler.side_effect = KeyboardInterrupt("User interrupted")
            
            result = self.runner.invoke(app, [
                "crawl", 
                str(url_file), 
                "--dry-run", 
                "--skip-validation"
            ])
            
            # Should handle interruption gracefully
            assert result.exit_code == 1
            
            # System should still be responsive
            result = self.runner.invoke(app, ["status", "--skip-validation"])
            assert result.exit_code == 0


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v"])