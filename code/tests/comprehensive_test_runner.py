import os
import sys
import subprocess
import json
import time
from datetime import datetime

class ComprehensiveTestRunner:
    def __init__(self, project_root):
        self.project_root = project_root
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'skipped_tests': 0,
            'modules_tested': [],
            'execution_time': 0,
            'coverage_report': {}
        }

    def run_tests(self, specific_module=None):
        """Run comprehensive test suite"""
        start_time = time.time()
        
        # Prepare test command
        cmd = ['python', '-m', 'coverage', 'run', '--source=.', 'manage.py', 'test']
        
        if specific_module:
            cmd.append(specific_module)
        
        # Run tests
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Calculate execution time
        self.test_results['execution_time'] = time.time() - start_time
        
        # Parse test output
        self._parse_test_output(result.stdout)
        
        # Generate coverage report
        self._generate_coverage_report()
        
        return self.test_results

    def _parse_test_output(self, output):
        """Parse test output and extract key metrics"""
        lines = output.split('\n')
        
        for line in lines:
            if 'test' in line.lower():
                if 'ok' in line.lower():
                    self.test_results['passed_tests'] += 1
                elif 'fail' in line.lower():
                    self.test_results['failed_tests'] += 1
                elif 'skip' in line.lower():
                    self.test_results['skipped_tests'] += 1
        
        # Extract total tests
        for line in lines:
            if 'Ran' in line and 'tests' in line:
                parts = line.split()
                self.test_results['total_tests'] = int(parts[1])
                break

    def _generate_coverage_report(self):
        """Generate detailed coverage report"""
        # Run coverage report
        coverage_result = subprocess.run(
            ['python', '-m', 'coverage', 'json', '-o', 'coverage.json'], 
            capture_output=True, text=True
        )
        
        # Read coverage data
        with open('coverage.json', 'r') as f:
            coverage_data = json.load(f)
        
        # Process coverage data
        self.test_results['coverage_report'] = {
            'total_statements': 0,
            'total_missing': 0,
            'coverage_percentage': 0,
            'module_coverage': {}
        }
        
        for module, data in coverage_data['files'].items():
            total_statements = data['summary']['num_statements']
            missing_lines = data['summary']['missing_lines']
            coverage_percent = (total_statements - missing_lines) / total_statements * 100
            
            self.test_results['coverage_report']['module_coverage'][module] = {
                'total_statements': total_statements,
                'missing_lines': missing_lines,
                'coverage_percentage': coverage_percent
            }
            
            self.test_results['coverage_report']['total_statements'] += total_statements
            self.test_results['coverage_report']['total_missing'] += missing_lines
        
        # Calculate overall coverage
        total_statements = self.test_results['coverage_report']['total_statements']
        total_missing = self.test_results['coverage_report']['total_missing']
        self.test_results['coverage_report']['coverage_percentage'] = (total_statements - total_missing) / total_statements * 100

    def generate_report(self):
        """Generate a comprehensive test report"""
        report = f"""
🧪 Comprehensive Test Report
===========================
Timestamp: {self.test_results['timestamp']}

Test Execution Summary:
----------------------
Total Tests: {self.test_results['total_tests']}
Passed Tests: {self.test_results['passed_tests']}
Failed Tests: {self.test_results['failed_tests']}
Skipped Tests: {self.test_results['skipped_tests']}
Execution Time: {self.test_results['execution_time']:.2f} seconds

Coverage Report:
---------------
Total Statements: {self.test_results['coverage_report']['total_statements']}
Missing Lines: {self.test_results['coverage_report']['total_missing']}
Overall Coverage: {self.test_results['coverage_report']['coverage_percentage']:.2f}%

Module Coverage Details:
-----------------------
"""
        for module, details in self.test_results['coverage_report']['module_coverage'].items():
            report += f"{module}:\n"
            report += f"  Total Statements: {details['total_statements']}\n"
            report += f"  Missing Lines: {details['missing_lines']}\n"
            report += f"  Coverage: {details['coverage_percentage']:.2f}%\n\n"
        
        # Save report
        with open('test_report.txt', 'w') as f:
            f.write(report)
        
        print(report)

def main():
    project_root = os.path.dirname(os.path.abspath(__file__))
    runner = ComprehensiveTestRunner(project_root)
    
    # Run tests
    runner.run_tests()
    
    # Generate report
    runner.generate_report()

if __name__ == '__main__':
    main() 