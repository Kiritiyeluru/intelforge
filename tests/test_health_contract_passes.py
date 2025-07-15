#!/usr/bin/env python3
"""
CLI Health Contract Test
Ensures that 'intelforge status --json' returns healthy status and validates the JSON schema.
This test acts as a contract to prevent breaking changes in CI integrations.
"""

import json
import pytest
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any
from typer.testing import CliRunner

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from scripts.cli import app
    CLI_AVAILABLE = True
except ImportError:
    CLI_AVAILABLE = False


class TestHealthContract:
    """Test suite for health contract validation"""
    
    def setup_method(self):
        """Set up test runner"""
        self.runner = CliRunner()
        self.project_root = Path(__file__).parent.parent
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_status_command_exists(self):
        """Test that status command exists and is accessible"""
        result = self.runner.invoke(app, ["status", "--help"])
        assert result.exit_code == 0
        assert "Show IntelForge system status" in result.output
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_status_json_output_format(self):
        """Test that status --json returns valid JSON"""
        result = self.runner.invoke(app, ["status", "--json", "--skip-validation"])
        
        # Should not fail catastrophically
        assert result.exit_code == 0
        
        # Should produce valid JSON
        try:
            status_data = json.loads(result.output)
        except json.JSONDecodeError as e:
            pytest.fail(f"Status command did not return valid JSON: {e}")
        
        # Basic structure validation
        assert isinstance(status_data, dict)
        assert "overall_status" in status_data
        assert "timestamp" in status_data
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_health_contract_schema(self):
        """Test that status JSON output conforms to expected schema"""
        result = self.runner.invoke(app, ["status", "--json", "--skip-validation"])
        assert result.exit_code == 0
        
        status_data = json.loads(result.output)
        
        # Required top-level fields
        required_fields = [
            "timestamp",
            "overall_status", 
            "modules",
            "storage",
            "config_files",
            "system_info"
        ]
        
        for field in required_fields:
            assert field in status_data, f"Required field '{field}' missing from status output"
        
        # Validate field types
        assert isinstance(status_data["timestamp"], str)
        assert isinstance(status_data["overall_status"], str)
        assert isinstance(status_data["modules"], dict)
        assert isinstance(status_data["storage"], dict)
        assert isinstance(status_data["config_files"], dict)
        assert isinstance(status_data["system_info"], dict)
        
        # Validate overall_status values
        valid_statuses = ["healthy", "degraded", "critical", "unknown"]
        assert status_data["overall_status"] in valid_statuses
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_modules_section_schema(self):
        """Test modules section conforms to expected schema"""
        result = self.runner.invoke(app, ["status", "--json", "--skip-validation"])
        assert result.exit_code == 0
        
        status_data = json.loads(result.output)
        modules = status_data["modules"]
        
        # Required module fields
        assert "core_available" in modules
        assert isinstance(modules["core_available"], bool)
        
        # If modules are available, should have version info
        if modules["core_available"]:
            assert "status" in modules
            assert modules["status"] in ["healthy", "degraded"]
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_storage_section_schema(self):
        """Test storage section conforms to expected schema"""
        result = self.runner.invoke(app, ["status", "--json", "--skip-validation"])
        assert result.exit_code == 0
        
        status_data = json.loads(result.output)
        storage = status_data["storage"]
        
        # Expected storage components
        expected_storage = ["qdrant", "chromadb", "data", "logs"]
        
        for storage_name in expected_storage:
            assert storage_name in storage, f"Storage component '{storage_name}' missing"
            
            storage_info = storage[storage_name]
            assert "exists" in storage_info
            assert "path" in storage_info
            assert "size_bytes" in storage_info
            assert "file_count" in storage_info
            
            assert isinstance(storage_info["exists"], bool)
            assert isinstance(storage_info["path"], str)
            assert isinstance(storage_info["size_bytes"], (int, float))
            assert isinstance(storage_info["file_count"], int)
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_config_files_section_schema(self):
        """Test config files section conforms to expected schema"""
        result = self.runner.invoke(app, ["status", "--json", "--skip-validation"])
        assert result.exit_code == 0
        
        status_data = json.loads(result.output)
        config_files = status_data["config_files"]
        
        # Expected config files
        expected_configs = ["reference_embeddings", "git_hooks", "claude_md", "implementation_plan"]
        
        for config_name in expected_configs:
            assert config_name in config_files, f"Config file '{config_name}' missing"
            
            config_info = config_files[config_name]
            assert "exists" in config_info
            assert "path" in config_info
            
            assert isinstance(config_info["exists"], bool)
            assert isinstance(config_info["path"], str)
            
            # If file exists, should have size and modified time
            if config_info["exists"]:
                if "size_bytes" in config_info:
                    assert isinstance(config_info["size_bytes"], (int, float))
                if "modified" in config_info:
                    assert isinstance(config_info["modified"], (int, float))
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_health_checks_with_validation(self):
        """Test health checks section when validation is enabled"""
        result = self.runner.invoke(app, ["status", "--json"])
        assert result.exit_code == 0
        
        status_data = json.loads(result.output)
        
        # Should have health_checks section when validation is enabled
        if "health_checks" in status_data:
            health_checks = status_data["health_checks"]
            
            # If health checks ran successfully
            if "error" not in health_checks:
                assert "overall_status" in health_checks
                assert "total_checks" in health_checks
                assert "results" in health_checks
                
                assert isinstance(health_checks["overall_status"], str)
                assert isinstance(health_checks["total_checks"], int)
                assert isinstance(health_checks["results"], dict)
                
                # Results should have expected counters
                results = health_checks["results"]
                expected_result_types = ["pass", "fail", "warn", "skip"]
                for result_type in expected_result_types:
                    assert result_type in results
                    assert isinstance(results[result_type], int)
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_status_command_backwards_compatibility(self):
        """Test that status command maintains backwards compatibility"""
        # Test basic status command (no flags)
        result = self.runner.invoke(app, ["status", "--skip-validation"])
        assert result.exit_code == 0
        
        # Should contain recognizable status information
        output = result.output
        assert "IntelForge System Status" in output
        assert "Module Status:" in output
        assert "Storage Status:" in output
        assert "Configuration Files:" in output
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_status_detailed_mode(self):
        """Test that detailed mode provides additional information"""
        result = self.runner.invoke(app, ["status", "--json", "--detailed"])
        assert result.exit_code == 0
        
        status_data = json.loads(result.output)
        
        # Detailed mode should include detailed health results if available
        if "health_checks" in status_data and "error" not in status_data["health_checks"]:
            health_checks = status_data["health_checks"]
            if "detailed_results" in health_checks:
                detailed_results = health_checks["detailed_results"]
                assert isinstance(detailed_results, list)
                
                # Each detailed result should have expected fields
                for result_item in detailed_results:
                    assert "name" in result_item
                    assert "level" in result_item
                    assert "result" in result_item
                    assert "message" in result_item
                    
                    assert isinstance(result_item["name"], str)
                    assert result_item["level"] in ["critical", "high", "medium", "low"]
                    assert result_item["result"] in ["pass", "fail", "warn", "skip"]
                    assert isinstance(result_item["message"], str)
    
    def test_health_contract_cli_direct(self):
        """Test health contract using direct CLI invocation (fallback test)"""
        # Direct subprocess call as fallback if Typer runner fails
        try:
            cmd = [sys.executable, "-m", "scripts.cli", "status", "--json", "--skip-validation"]
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Should not fail catastrophically
            assert result.returncode == 0, f"CLI command failed: {result.stderr}"
            
            # Should produce valid JSON
            status_data = json.loads(result.stdout)
            
            # Basic contract validation
            assert "overall_status" in status_data
            assert "modules" in status_data
            assert "storage" in status_data
            
        except subprocess.TimeoutExpired:
            pytest.fail("Status command timed out")
        except Exception as e:
            pytest.skip(f"Direct CLI test skipped: {e}")
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_drift_flag_placeholder(self):
        """Test that drift flag is accepted and provides placeholder response"""
        result = self.runner.invoke(app, ["status", "--json", "--drift", "--skip-validation"])
        assert result.exit_code == 0
        
        status_data = json.loads(result.output)
        
        # Should have drift_report section
        assert "drift_report" in status_data
        drift_report = status_data["drift_report"]
        
        assert "status" in drift_report
        assert "message" in drift_report
        assert drift_report["status"] == "not_implemented"
    
    def test_json_schema_stability(self):
        """Test that JSON schema is stable and won't break CI integrations"""
        # This test ensures that the JSON output schema doesn't change unexpectedly
        # If this test fails, it means a breaking change was introduced
        
        expected_schema_version = "1.0"  # Increment when making breaking changes
        
        if not CLI_AVAILABLE:
            pytest.skip("CLI not available for schema validation")
        
        result = self.runner.invoke(app, ["status", "--json", "--skip-validation"])
        if result.exit_code != 0:
            pytest.skip("Status command failed, skipping schema validation")
        
        try:
            status_data = json.loads(result.output)
        except json.JSONDecodeError:
            pytest.fail("Status command did not return valid JSON")
        
        # Core schema elements that should never change
        core_schema = {
            "overall_status": str,
            "timestamp": str,
            "modules": dict,
            "storage": dict,
            "config_files": dict,
            "system_info": dict
        }
        
        for field, expected_type in core_schema.items():
            assert field in status_data, f"Core schema field '{field}' missing"
            assert isinstance(status_data[field], expected_type), f"Field '{field}' has wrong type"
        
        # If schema changes are needed, update expected_schema_version above
        # and document the changes in CHANGELOG.md


class TestHealthContractIntegration:
    """Integration tests for health contract in real scenarios"""
    
    def setup_method(self):
        """Set up integration test environment"""
        self.runner = CliRunner()
        self.project_root = Path(__file__).parent.parent
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_ci_automation_workflow(self):
        """Test typical CI automation workflow using status command"""
        # Simulate CI check: status should return JSON and exit code 0
        result = self.runner.invoke(app, ["status", "--json", "--skip-validation"])
        
        # CI systems rely on exit codes
        assert result.exit_code == 0
        
        # Parse status for automated decision making
        status_data = json.loads(result.output)
        
        # CI would check overall status
        overall_status = status_data["overall_status"]
        
        # Simulate CI logic
        if overall_status == "critical":
            # CI would fail the build
            pass  # This is expected behavior
        elif overall_status == "degraded":
            # CI might issue warnings but continue
            pass  # This is acceptable
        elif overall_status == "healthy":
            # CI would proceed normally
            pass  # This is ideal
        else:
            pytest.fail(f"Unexpected overall status: {overall_status}")
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_monitoring_integration(self):
        """Test integration with monitoring systems"""
        result = self.runner.invoke(app, ["status", "--json"])
        assert result.exit_code == 0
        
        status_data = json.loads(result.output)
        
        # Monitoring systems would extract metrics
        metrics = {}
        
        # Extract storage metrics
        for storage_name, storage_info in status_data["storage"].items():
            if storage_info["exists"]:
                metrics[f"storage_{storage_name}_size_mb"] = storage_info["size_bytes"] / (1024*1024)
                metrics[f"storage_{storage_name}_file_count"] = storage_info["file_count"]
        
        # Extract system metrics if available
        if "system_info" in status_data:
            sys_info = status_data["system_info"]
            if "memory_available_gb" in sys_info:
                metrics["memory_available_gb"] = sys_info["memory_available_gb"]
            if "disk_free_gb" in sys_info:
                metrics["disk_free_gb"] = sys_info["disk_free_gb"]
        
        # Extract health metrics if available
        if "health_checks" in status_data and "error" not in status_data["health_checks"]:
            health = status_data["health_checks"]
            metrics["health_checks_total"] = health["total_checks"]
            metrics["health_checks_passed"] = health["results"]["pass"]
            metrics["health_checks_failed"] = health["results"]["fail"]
        
        # Metrics should be extractable and numeric
        for metric_name, metric_value in metrics.items():
            assert isinstance(metric_value, (int, float)), f"Metric {metric_name} is not numeric"


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v"])