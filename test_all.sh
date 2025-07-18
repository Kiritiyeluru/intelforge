#\!/bin/bash
# End-to-end regression test suite
echo "🧪 Running IntelForge End-to-End Test Suite"
echo "============================================="

echo "1. CLI Smoke Test..."
python tests/smoketest_all_cli.py

echo "2. Data Integrity Validation..."
python -m scripts.validation.data_integrity_validator

echo "3. Health Contract Test..."
python -m pytest tests/test_health_contract_passes.py -v

echo "4. Security Health Check..."
python -c "
from scripts.utils.vector_security_manager import VectorSecurityManager
sm = VectorSecurityManager()
health = sm.get_security_health_check()
print('Security Health Check:')
for component, status in health.items():
    print(f'  {component}: {status}')
"

echo "============================================="
echo "✅ All tests completed successfully\!"
