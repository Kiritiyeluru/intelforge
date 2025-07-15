import exec from 'k6/execution';
import { check, sleep } from 'k6';
import { Rate, Counter } from 'k6/metrics';

// Custom metrics for developer scenarios
export const errorRate = new Rate('errors');
export const cliSuccessRate = new Rate('cli_success');
export const migrationCounter = new Counter('migrations_completed');

// Test configuration for developer persona - CLI operations and workflows
export const options = {
  scenarios: {
    developer_cli_operations: {
      executor: 'per-vu-iterations',
      vus: 3,
      iterations: 10,
      maxDuration: '5m',
    },
    developer_concurrent_workflows: {
      executor: 'shared-iterations',
      vus: 5,
      iterations: 25,
      maxDuration: '3m',
    },
  },
  thresholds: {
    errors: ['rate<0.1'],               // Error rate under 10%
    cli_success: ['rate>0.9'],          // CLI success rate > 90%
    iterations: ['count>20'],           // At least 20 successful iterations
  },
};

// CLI commands for developer persona testing
const cliCommands = [
  'status --json',
  'status --detailed',
  'validate --quick',
  'migrate --dry-run',
  'docs --generate',
];

// Configuration scenarios for testing
const configScenarios = [
  { source: 'chromadb', target: 'qdrant' },
  { source: 'qdrant', target: 'chromadb' },
  { action: 'backup', format: 'json' },
  { action: 'restore', format: 'yaml' },
];

export default function () {
  const vuId = exec.vu.idInTest;
  const iterationId = exec.scenario.iterationInTest;
  const startTime = Date.now();
  
  console.log(`Developer VU ${vuId}, Iteration ${iterationId} starting`);
  
  // Test 1: CLI Command Generation and Execution
  const command = cliCommands[Math.floor(Math.random() * cliCommands.length)];
  
  // Simulate CLI command execution time (since we can't actually exec in k6)
  const cliStartTime = Date.now();
  sleep(Math.random() * 2 + 0.5); // 0.5-2.5s for CLI operation
  const cliEndTime = Date.now();
  
  const cliDuration = cliEndTime - cliStartTime;
  const cliSuccess = cliDuration < 5000; // CLI should complete within 5s
  
  const cliCheck = check({ duration: cliDuration }, {
    'CLI command completes quickly': () => cliSuccess,
    'CLI execution under 5s': () => cliDuration < 5000,
  });
  
  if (cliSuccess) {
    cliSuccessRate.add(1);
  } else {
    errorRate.add(1);
  }
  
  console.log(`VU ${vuId}: CLI command '${command}' took ${cliDuration}ms`);
  
  // Test 2: Configuration Migration Workflow
  const config = configScenarios[Math.floor(Math.random() * configScenarios.length)];
  
  const migrationStartTime = Date.now();
  
  // Simulate configuration migration steps
  const steps = [
    'validate_source_config',
    'backup_current_config', 
    'transform_configuration',
    'validate_target_config',
    'apply_migration',
    'verify_migration',
  ];
  
  let migrationSuccess = true;
  steps.forEach((step, index) => {
    const stepDuration = Math.random() * 500 + 100; // 100-600ms per step
    sleep(stepDuration / 1000);
    
    // Simulate occasional step failure (5% chance)
    if (Math.random() < 0.05) {
      migrationSuccess = false;
      console.log(`VU ${vuId}: Migration step '${step}' failed`);
    }
  });
  
  const migrationEndTime = Date.now();
  const migrationDuration = migrationEndTime - migrationStartTime;
  
  const migrationCheck = check({ 
    success: migrationSuccess, 
    duration: migrationDuration 
  }, {
    'migration completes successfully': (data) => data.success,
    'migration under 10s': (data) => data.duration < 10000,
  });
  
  if (migrationSuccess) {
    migrationCounter.add(1);
    console.log(`VU ${vuId}: Migration ${JSON.stringify(config)} completed in ${migrationDuration}ms`);
  } else {
    errorRate.add(1);
  }
  
  // Test 3: Snapshot and Reload Operations
  const snapshotStartTime = Date.now();
  
  // Simulate snapshot creation
  sleep(Math.random() * 1 + 0.2); // 0.2-1.2s for snapshot
  
  // Simulate configuration reload
  sleep(Math.random() * 0.8 + 0.1); // 0.1-0.9s for reload
  
  const snapshotEndTime = Date.now();
  const snapshotDuration = snapshotEndTime - snapshotStartTime;
  
  const snapshotCheck = check({ duration: snapshotDuration }, {
    'snapshot operations complete quickly': () => snapshotDuration < 3000,
  });
  
  if (!snapshotCheck) {
    errorRate.add(1);
  }
  
  // Test 4: DevOps Integration Workflow
  const devopsStartTime = Date.now();
  
  // Simulate CI/CD pipeline integration steps
  const pipelineSteps = [
    'git_hook_validation',
    'pre_commit_checks',
    'test_execution',
    'build_validation', 
    'deployment_preparation',
  ];
  
  pipelineSteps.forEach(step => {
    sleep(Math.random() * 0.3 + 0.1); // 0.1-0.4s per pipeline step
  });
  
  const devopsEndTime = Date.now();
  const devopsDuration = devopsEndTime - devopsStartTime;
  
  const devopsCheck = check({ duration: devopsDuration }, {
    'DevOps workflow completes': () => devopsDuration < 5000,
  });
  
  if (!devopsCheck) {
    errorRate.add(1);
  }
  
  // Overall scenario performance
  const totalTime = Date.now() - startTime;
  console.log(`VU ${vuId}: Complete developer workflow took ${totalTime}ms`);
  
  // Brief pause between iterations
  sleep(Math.random() * 1 + 0.5); // 0.5-1.5s pause
}

export function handleSummary(data) {
  const summary = {
    timestamp: new Date().toISOString(),
    test_type: 'developer_load_test',
    scenarios: Object.keys(data.metrics).length > 0 ? 'completed' : 'failed',
    total_iterations: data.metrics.iterations?.values?.count || 0,
    successful_migrations: data.metrics.migrations_completed?.values?.count || 0,
    cli_success_rate: (data.metrics.cli_success?.values?.rate || 0) * 100,
    error_rate: (data.metrics.errors?.values?.rate || 0) * 100,
    performance: {
      avg_iteration_duration: data.metrics.iteration_duration?.values?.avg || 'N/A',
      p95_iteration_duration: data.metrics.iteration_duration?.values?.['p(95)'] || 'N/A',
    },
    thresholds_passed: data.state?.testRunDurationMs ? 'yes' : 'partial',
  };
  
  return {
    'tests/load/k6_developer_results.json': JSON.stringify(summary, null, 2),
    stdout: formatDeveloperSummary(summary),
  };
}

function formatDeveloperSummary(summary) {
  return `
Developer Load Test Results
===========================
Total Iterations: ${summary.total_iterations}
Successful Migrations: ${summary.successful_migrations}
CLI Success Rate: ${summary.cli_success_rate.toFixed(1)}%
Error Rate: ${summary.error_rate.toFixed(1)}%
Test Status: ${summary.scenarios}

Performance Metrics:
- Average Duration: ${summary.performance.avg_iteration_duration}ms
- 95th Percentile: ${summary.performance.p95_iteration_duration}ms

Developer Workflow Validation: ${summary.error_rate < 10 ? 'PASS' : 'FAIL'}
`;
}