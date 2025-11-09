import os
import sys
import subprocess
import json

class TestCoverageImprover:
    def __init__(self, project_root):
        self.project_root = project_root
        self.coverage_data = {}

    def run_coverage_analysis(self):
        """Run comprehensive coverage analysis"""
        print("🔍 Running comprehensive coverage analysis...")
        result = subprocess.run(
            ['python', '-m', 'coverage', 'json', '-o', 'coverage.json'],
            capture_output=True, text=True
        )
        
        with open('coverage.json', 'r') as f:
            self.coverage_data = json.load(f)

    def identify_low_coverage_modules(self, threshold=50):
        """Identify modules with low test coverage"""
        low_coverage_modules = []
        
        for module, data in self.coverage_data['files'].items():
            # Skip modules with zero statements
            if data['summary']['num_statements'] == 0:
                continue
            
            try:
                coverage_percent = (data['summary']['num_statements'] - data['summary']['missing_lines']) / data['summary']['num_statements'] * 100
            except ZeroDivisionError:
                continue
            
            if coverage_percent < threshold:
                low_coverage_modules.append({
                    'module': module,
                    'coverage': coverage_percent,
                    'missing_lines': data['summary']['missing_lines'],
                    'total_lines': data['summary']['num_statements']
                })
        
        return sorted(low_coverage_modules, key=lambda x: x['coverage'])

    def generate_test_template(self, module_info):
        """Generate a test template for a given module"""
        module_path = module_info['module']
        module_name = os.path.splitext(os.path.basename(module_path))[0]
        test_file_path = os.path.join(
            os.path.dirname(module_path), 
            f'test_{module_name}.py'
        )
        
        template = f'''
import pytest
from {module_name} import *

class Test{module_name.capitalize()}:
    def test_basic_functionality(self):
        """Basic sanity test for {module_name} module"""
        assert True, "Initial test setup"

    # TODO: Add specific test cases for {module_name} module
    # Coverage Details:
    # Total Lines: {module_info['total_lines']}
    # Missing Lines: {module_info['missing_lines']}
    # Current Coverage: {module_info['coverage']:.2f}%
'''
        
        with open(test_file_path, 'w') as f:
            f.write(template)
        
        print(f"✅ Generated test template for {module_name} at {test_file_path}")

    def recommend_improvements(self, low_coverage_modules):
        """Provide recommendations for improving test coverage"""
        print("\n🚀 Test Coverage Improvement Recommendations:")
        for module in low_coverage_modules:
            print(f"\nModule: {module['module']}")
            print(f"Current Coverage: {module['coverage']:.2f}%")
            print(f"Total Lines: {module['total_lines']}")
            print(f"Missing Lines: {module['missing_lines']}")
            print("Suggested Actions:")
            print("1. Create comprehensive unit tests")
            print("2. Test edge cases and error scenarios")
            print("3. Add integration tests")
            print("4. Verify all code paths are exercised")

    def run(self):
        """Main execution method"""
        os.chdir(self.project_root)
        
        # Run tests and generate coverage report
        subprocess.run(['python', '-m', 'coverage', 'run', '--source=.', 'manage.py', 'test'])
        
        # Analyze coverage
        self.run_coverage_analysis()
        
        # Find low coverage modules
        low_coverage_modules = self.identify_low_coverage_modules()
        
        # Provide recommendations
        self.recommend_improvements(low_coverage_modules)
        
        # Generate test templates for low coverage modules
        for module in low_coverage_modules[:5]:  # Limit to top 5
            self.generate_test_template(module)

def main():
    project_root = os.path.dirname(os.path.abspath(__file__))
    improver = TestCoverageImprover(project_root)
    improver.run()

if __name__ == '__main__':
    main() 