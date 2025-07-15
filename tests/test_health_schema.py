#!/usr/bin/env python3
"""
Health Schema Validator using Pydantic
Ensures the JSON output schema from 'intelforge status --json' is validated and prevents breaking changes.
Uses Pydantic models to define and validate the expected schema structure.
"""

import json
import pytest
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, validator
from typer.testing import CliRunner

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from scripts.cli import app
    CLI_AVAILABLE = True
except ImportError:
    CLI_AVAILABLE = False

try:
    from pydantic import BaseModel
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False


# Pydantic models for schema validation
class ModulesSchema(BaseModel):
    """Schema for modules section"""
    core_available: bool
    status: Optional[str] = None
    semantic_crawler_version: Optional[str] = None
    
    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            assert v in ['healthy', 'degraded'], f"Invalid module status: {v}"
        return v


class StorageItemSchema(BaseModel):
    """Schema for individual storage item"""
    exists: bool
    path: str
    size_bytes: int = Field(ge=0)  # Must be non-negative
    file_count: int = Field(ge=0)  # Must be non-negative


class StorageSchema(BaseModel):
    """Schema for storage section"""
    qdrant: StorageItemSchema
    chromadb: StorageItemSchema
    data: StorageItemSchema
    logs: StorageItemSchema


class ConfigFileItemSchema(BaseModel):
    """Schema for individual config file item"""
    exists: bool
    path: str
    size_bytes: Optional[int] = Field(None, ge=0)
    modified: Optional[float] = None


class ConfigFilesSchema(BaseModel):
    """Schema for config files section"""
    reference_embeddings: ConfigFileItemSchema
    git_hooks: ConfigFileItemSchema
    claude_md: ConfigFileItemSchema
    implementation_plan: ConfigFileItemSchema


class SystemInfoSchema(BaseModel):
    """Schema for system info section"""
    python_version: Optional[str] = None
    memory_available_gb: Optional[float] = Field(None, ge=0)
    disk_free_gb: Optional[float] = Field(None, ge=0)
    cpu_count: Optional[int] = Field(None, ge=1)


class HealthResultsSchema(BaseModel):
    """Schema for health check results counters"""
    pass_: int = Field(alias='pass', ge=0)
    fail: int = Field(ge=0)
    warn: int = Field(ge=0)
    skip: int = Field(ge=0)


class HealthCheckDetailSchema(BaseModel):
    """Schema for individual health check detail"""
    name: str
    level: str
    result: str
    message: str
    fix_suggestion: Optional[str] = None
    
    @validator('level')
    def validate_level(cls, v):
        assert v in ['critical', 'high', 'medium', 'low'], f"Invalid level: {v}"
        return v
    
    @validator('result')
    def validate_result(cls, v):
        assert v in ['pass', 'fail', 'warn', 'skip'], f"Invalid result: {v}"
        return v


class HealthChecksSchema(BaseModel):
    """Schema for health checks section"""
    overall_status: Optional[str] = None
    total_checks: Optional[int] = Field(None, ge=0)
    results: Optional[HealthResultsSchema] = None
    critical_failures: Optional[int] = Field(None, ge=0)
    detailed_results: Optional[List[HealthCheckDetailSchema]] = None
    error: Optional[str] = None
    
    @validator('overall_status')
    def validate_overall_status(cls, v):
        if v is not None:
            valid_statuses = ['healthy', 'warning', 'failure', 'critical_failure', 'error']
            assert v in valid_statuses, f"Invalid overall_status: {v}"
        return v


class DriftReportSchema(BaseModel):
    """Schema for drift report section"""
    status: str
    message: str
    
    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['not_implemented', 'available', 'error']
        assert v in valid_statuses, f"Invalid drift status: {v}"
        return v


class IntelForgeStatusSchema(BaseModel):
    """Complete schema for IntelForge status JSON output"""
    timestamp: str
    overall_status: str
    modules: ModulesSchema
    storage: StorageSchema
    config_files: ConfigFilesSchema
    system_info: SystemInfoSchema
    health_checks: Optional[HealthChecksSchema] = None
    drift_report: Optional[DriftReportSchema] = None
    
    @validator('overall_status')
    def validate_overall_status(cls, v):
        valid_statuses = ['healthy', 'degraded', 'critical', 'unknown']
        assert v in valid_statuses, f"Invalid overall_status: {v}"
        return v
    
    @validator('timestamp')
    def validate_timestamp(cls, v):
        # Basic ISO format validation
        assert 'T' in v, "Timestamp should be in ISO format"
        return v


@pytest.mark.health
@pytest.mark.regression
@pytest.mark.critical
class TestHealthSchema:
    """Test suite for health schema validation using Pydantic"""
    
    def setup_method(self):
        """Set up test runner"""
        self.runner = CliRunner()
        self.project_root = Path(__file__).parent.parent
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    @pytest.mark.skipif(not PYDANTIC_AVAILABLE, reason="Pydantic not available")
    @pytest.mark.quick
    @pytest.mark.cli
    def test_basic_schema_validation(self):
        """Test basic schema validation with minimal data"""
        result = self.runner.invoke(app, ["status", "--json", "--skip-validation"])
        assert result.exit_code == 0
        
        status_data = json.loads(result.output)
        
        # Validate against Pydantic schema
        try:
            validated_status = IntelForgeStatusSchema(**status_data)
            assert validated_status is not None
        except Exception as e:
            pytest.fail(f"Schema validation failed: {e}")
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available") 
    @pytest.mark.skipif(not PYDANTIC_AVAILABLE, reason="Pydantic not available")
    def test_modules_schema_validation(self):
        """Test modules section schema validation"""
        result = self.runner.invoke(app, ["status", "--json", "--skip-validation"])
        assert result.exit_code == 0
        
        status_data = json.loads(result.output)
        
        # Validate modules section specifically
        try:
            modules_schema = ModulesSchema(**status_data["modules"])
            assert isinstance(modules_schema.core_available, bool)
            if modules_schema.status:
                assert modules_schema.status in ['healthy', 'degraded']
        except Exception as e:
            pytest.fail(f"Modules schema validation failed: {e}")
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    @pytest.mark.skipif(not PYDANTIC_AVAILABLE, reason="Pydantic not available")
    def test_storage_schema_validation(self):
        """Test storage section schema validation"""
        result = self.runner.invoke(app, ["status", "--json", "--skip-validation"])
        assert result.exit_code == 0
        
        status_data = json.loads(result.output)
        
        # Validate storage section specifically
        try:
            storage_schema = StorageSchema(**status_data["storage"])
            
            # Validate each storage component
            for storage_name in ['qdrant', 'chromadb', 'data', 'logs']:
                storage_item = getattr(storage_schema, storage_name)
                assert isinstance(storage_item.exists, bool)
                assert isinstance(storage_item.path, str)
                assert storage_item.size_bytes >= 0
                assert storage_item.file_count >= 0
                
        except Exception as e:
            pytest.fail(f"Storage schema validation failed: {e}")
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    @pytest.mark.skipif(not PYDANTIC_AVAILABLE, reason="Pydantic not available")
    def test_config_files_schema_validation(self):
        """Test config files section schema validation"""
        result = self.runner.invoke(app, ["status", "--json", "--skip-validation"])
        assert result.exit_code == 0
        
        status_data = json.loads(result.output)
        
        # Validate config files section specifically
        try:
            config_schema = ConfigFilesSchema(**status_data["config_files"])
            
            # Validate each config file
            for config_name in ['reference_embeddings', 'git_hooks', 'claude_md', 'implementation_plan']:
                config_item = getattr(config_schema, config_name)
                assert isinstance(config_item.exists, bool)
                assert isinstance(config_item.path, str)
                
                # If file exists and has size_bytes, it should be non-negative
                if config_item.size_bytes is not None:
                    assert config_item.size_bytes >= 0
                    
        except Exception as e:
            pytest.fail(f"Config files schema validation failed: {e}")
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    @pytest.mark.skipif(not PYDANTIC_AVAILABLE, reason="Pydantic not available")
    def test_system_info_schema_validation(self):
        """Test system info section schema validation"""
        result = self.runner.invoke(app, ["status", "--json", "--skip-validation"])
        assert result.exit_code == 0
        
        status_data = json.loads(result.output)
        
        # Validate system info section specifically
        try:
            system_schema = SystemInfoSchema(**status_data["system_info"])
            
            # Validate numeric fields are positive if present
            if system_schema.memory_available_gb is not None:
                assert system_schema.memory_available_gb >= 0
            if system_schema.disk_free_gb is not None:
                assert system_schema.disk_free_gb >= 0
            if system_schema.cpu_count is not None:
                assert system_schema.cpu_count >= 1
                
        except Exception as e:
            pytest.fail(f"System info schema validation failed: {e}")
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    @pytest.mark.skipif(not PYDANTIC_AVAILABLE, reason="Pydantic not available")
    def test_health_checks_schema_validation(self):
        """Test health checks section schema validation when enabled"""
        result = self.runner.invoke(app, ["status", "--json"])
        assert result.exit_code == 0
        
        status_data = json.loads(result.output)
        
        # Validate health checks section if present
        if "health_checks" in status_data:
            try:
                health_schema = HealthChecksSchema(**status_data["health_checks"])
                
                # If overall_status is present, validate it
                if health_schema.overall_status:
                    valid_statuses = ['healthy', 'warning', 'failure', 'critical_failure', 'error']
                    assert health_schema.overall_status in valid_statuses
                
                # If results are present, validate counters
                if health_schema.results:
                    assert health_schema.results.pass_ >= 0
                    assert health_schema.results.fail >= 0
                    assert health_schema.results.warn >= 0
                    assert health_schema.results.skip >= 0
                
                # If detailed results are present, validate each item
                if health_schema.detailed_results:
                    for detail in health_schema.detailed_results:
                        assert detail.level in ['critical', 'high', 'medium', 'low']
                        assert detail.result in ['pass', 'fail', 'warn', 'skip']
                        assert isinstance(detail.name, str)
                        assert isinstance(detail.message, str)
                        
            except Exception as e:
                pytest.fail(f"Health checks schema validation failed: {e}")
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    @pytest.mark.skipif(not PYDANTIC_AVAILABLE, reason="Pydantic not available")
    def test_detailed_mode_schema_validation(self):
        """Test schema validation in detailed mode"""
        result = self.runner.invoke(app, ["status", "--json", "--detailed"])
        assert result.exit_code == 0
        
        status_data = json.loads(result.output)
        
        # Validate complete schema
        try:
            validated_status = IntelForgeStatusSchema(**status_data)
            
            # In detailed mode, if health checks are present and successful,
            # we should have detailed_results
            if (validated_status.health_checks and 
                validated_status.health_checks.error is None and
                validated_status.health_checks.detailed_results):
                
                # Validate detailed results structure
                for detail in validated_status.health_checks.detailed_results:
                    assert detail.name
                    assert detail.level in ['critical', 'high', 'medium', 'low']
                    assert detail.result in ['pass', 'fail', 'warn', 'skip']
                    assert detail.message
                    
        except Exception as e:
            pytest.fail(f"Detailed mode schema validation failed: {e}")
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    @pytest.mark.skipif(not PYDANTIC_AVAILABLE, reason="Pydantic not available")
    def test_drift_flag_schema_validation(self):
        """Test schema validation with drift flag"""
        result = self.runner.invoke(app, ["status", "--json", "--drift", "--skip-validation"])
        assert result.exit_code == 0
        
        status_data = json.loads(result.output)
        
        # Validate drift report section
        if "drift_report" in status_data:
            try:
                drift_schema = DriftReportSchema(**status_data["drift_report"])
                assert drift_schema.status in ['not_implemented', 'available', 'error']
                assert isinstance(drift_schema.message, str)
            except Exception as e:
                pytest.fail(f"Drift report schema validation failed: {e}")
    
    @pytest.mark.skipif(not PYDANTIC_AVAILABLE, reason="Pydantic not available")
    def test_schema_edge_cases(self):
        """Test schema validation with edge cases and malformed data"""
        
        # Test with missing required fields
        invalid_data_missing = {
            "timestamp": "2023-01-01T00:00:00",
            # Missing overall_status and other required fields
        }
        
        with pytest.raises(Exception):
            IntelForgeStatusSchema(**invalid_data_missing)
        
        # Test with invalid overall_status
        invalid_data_status = {
            "timestamp": "2023-01-01T00:00:00",
            "overall_status": "invalid_status",
            "modules": {"core_available": True},
            "storage": {
                "qdrant": {"exists": True, "path": "/path", "size_bytes": 0, "file_count": 0},
                "chromadb": {"exists": True, "path": "/path", "size_bytes": 0, "file_count": 0},
                "data": {"exists": True, "path": "/path", "size_bytes": 0, "file_count": 0},
                "logs": {"exists": True, "path": "/path", "size_bytes": 0, "file_count": 0}
            },
            "config_files": {
                "reference_embeddings": {"exists": True, "path": "/path"},
                "git_hooks": {"exists": True, "path": "/path"},
                "claude_md": {"exists": True, "path": "/path"},
                "implementation_plan": {"exists": True, "path": "/path"}
            },
            "system_info": {}
        }
        
        with pytest.raises(Exception):
            IntelForgeStatusSchema(**invalid_data_status)
        
        # Test with negative values where they shouldn't be
        invalid_data_negative = {
            "timestamp": "2023-01-01T00:00:00",
            "overall_status": "healthy",
            "modules": {"core_available": True},
            "storage": {
                "qdrant": {"exists": True, "path": "/path", "size_bytes": -1, "file_count": 0},  # Invalid
                "chromadb": {"exists": True, "path": "/path", "size_bytes": 0, "file_count": 0},
                "data": {"exists": True, "path": "/path", "size_bytes": 0, "file_count": 0},
                "logs": {"exists": True, "path": "/path", "size_bytes": 0, "file_count": 0}
            },
            "config_files": {
                "reference_embeddings": {"exists": True, "path": "/path"},
                "git_hooks": {"exists": True, "path": "/path"},
                "claude_md": {"exists": True, "path": "/path"},
                "implementation_plan": {"exists": True, "path": "/path"}
            },
            "system_info": {}
        }
        
        with pytest.raises(Exception):
            IntelForgeStatusSchema(**invalid_data_negative)
    
    @pytest.mark.skipif(not PYDANTIC_AVAILABLE, reason="Pydantic not available")
    def test_schema_evolution_safety(self):
        """Test that schema can evolve safely without breaking existing integrations"""
        
        # Test that additional fields are accepted (forward compatibility)
        extended_data = {
            "timestamp": "2023-01-01T00:00:00",
            "overall_status": "healthy",
            "modules": {
                "core_available": True,
                "new_module_field": "should_be_ignored"  # New field
            },
            "storage": {
                "qdrant": {"exists": True, "path": "/path", "size_bytes": 0, "file_count": 0},
                "chromadb": {"exists": True, "path": "/path", "size_bytes": 0, "file_count": 0},
                "data": {"exists": True, "path": "/path", "size_bytes": 0, "file_count": 0},
                "logs": {"exists": True, "path": "/path", "size_bytes": 0, "file_count": 0},
                "new_storage_type": {"exists": True, "path": "/path", "size_bytes": 0, "file_count": 0}  # New storage
            },
            "config_files": {
                "reference_embeddings": {"exists": True, "path": "/path"},
                "git_hooks": {"exists": True, "path": "/path"},
                "claude_md": {"exists": True, "path": "/path"},
                "implementation_plan": {"exists": True, "path": "/path"}
            },
            "system_info": {
                "new_system_field": "should_be_ignored"  # New field
            },
            "new_top_level_section": {"data": "should_be_ignored"}  # New section
        }
        
        # This should work (schema should ignore extra fields)
        try:
            validated = IntelForgeStatusSchema(**extended_data)
            assert validated.overall_status == "healthy"
        except Exception as e:
            pytest.fail(f"Schema should accept additional fields for forward compatibility: {e}")
    
    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    @pytest.mark.skipif(not PYDANTIC_AVAILABLE, reason="Pydantic not available")
    def test_schema_consistency_across_runs(self):
        """Test that schema is consistent across multiple command runs"""
        
        # Run status command multiple times
        results = []
        for _ in range(3):
            result = self.runner.invoke(app, ["status", "--json", "--skip-validation"])
            assert result.exit_code == 0
            results.append(json.loads(result.output))
        
        # Validate all results against schema
        for i, status_data in enumerate(results):
            try:
                validated = IntelForgeStatusSchema(**status_data)
                assert validated is not None
            except Exception as e:
                pytest.fail(f"Schema validation failed for run {i+1}: {e}")
        
        # Check that core structure is consistent
        for i in range(1, len(results)):
            # Same top-level keys should be present
            assert set(results[0].keys()) == set(results[i].keys()), "Top-level keys changed between runs"
            
            # Module structure should be consistent
            assert set(results[0]["modules"].keys()) == set(results[i]["modules"].keys())
            
            # Storage structure should be consistent
            assert set(results[0]["storage"].keys()) == set(results[i]["storage"].keys())
            
            # Config files structure should be consistent
            assert set(results[0]["config_files"].keys()) == set(results[i]["config_files"].keys())


class TestSchemaBreakingChanges:
    """Test suite to detect breaking changes in the schema"""
    
    @pytest.mark.skipif(not PYDANTIC_AVAILABLE, reason="Pydantic not available")
    def test_schema_version_compatibility(self):
        """Test that current schema is compatible with expected baseline"""
        
        # This represents a baseline schema that CI systems might depend on
        baseline_status = {
            "timestamp": "2023-01-01T00:00:00.000000",
            "overall_status": "healthy",
            "modules": {
                "core_available": True,
                "status": "healthy"
            },
            "storage": {
                "qdrant": {"exists": False, "path": "/path/qdrant", "size_bytes": 0, "file_count": 0},
                "chromadb": {"exists": True, "path": "/path/chromadb", "size_bytes": 1024, "file_count": 1},
                "data": {"exists": True, "path": "/path/data", "size_bytes": 2048, "file_count": 5},
                "logs": {"exists": True, "path": "/path/logs", "size_bytes": 512, "file_count": 10}
            },
            "config_files": {
                "reference_embeddings": {"exists": True, "path": "/path/embeddings.json", "size_bytes": 1024},
                "git_hooks": {"exists": True, "path": "/path/hooks"},
                "claude_md": {"exists": False, "path": "/path/CLAUDE.md"},
                "implementation_plan": {"exists": True, "path": "/path/plan.md", "size_bytes": 2048}
            },
            "system_info": {
                "python_version": "3.8.0",
                "memory_available_gb": 4.0,
                "disk_free_gb": 50.0,
                "cpu_count": 4
            }
        }
        
        # This should always validate successfully - if it doesn't, we have a breaking change
        try:
            validated = IntelForgeStatusSchema(**baseline_status)
            assert validated.overall_status == "healthy"
        except Exception as e:
            pytest.fail(f"BREAKING CHANGE DETECTED: Baseline schema no longer validates: {e}")


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v"])