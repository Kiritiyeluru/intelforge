"""
Persona Testing Package - User-Centric Scenario Testing

This package contains comprehensive persona-based testing scenarios for IntelForge,
validating real-world user workflows and use cases.

Modules:
- test_researcher_scenario: Bulk semantic extraction from academic URLs
- test_trader_scenario: Financial data validation with anti-detection
- test_developer_scenario: CLI workflows and config migrations  
- test_e2e_workflow_templates: Automated E2E testing with fixture-based validation

Features:
- Persona-driven test scenarios
- Cross-persona workflow integration
- Performance benchmarking
- Error recovery testing
- Production readiness validation
"""

__version__ = "1.0.0"
__author__ = "IntelForge Testing Team"

# Import main test classes for easy access
from .test_researcher_scenario import TestResearcherPersona
from .test_trader_scenario import TestTraderPersona  
from .test_developer_scenario import TestDeveloperPersona
from .test_e2e_workflow_templates import TestE2EWorkflowTemplates

__all__ = [
    "TestResearcherPersona",
    "TestTraderPersona", 
    "TestDeveloperPersona",
    "TestE2EWorkflowTemplates"
]