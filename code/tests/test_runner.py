#!/usr/bin/env python
"""
Centralized Test Runner for Aevum Health Platform

This test runner provides comprehensive testing capabilities for the entire platform
with organized test execution by app, test type, and coverage reporting.

Usage:
    python tests/test_runner.py                    # Run all tests
    python tests/test_runner.py --app auth         # Run authentication tests only
    python tests/test_runner.py --type api         # Run API tests only
    python tests/test_runner.py --coverage         # Run with coverage report
    python tests/test_runner.py --fast             # Run fast tests only
    python tests/test_runner.py --integration      # Run integration tests only
"""

import os
import sys
import django
import time
import argparse
from django.conf import settings
from django.test.utils import get_runner
from django.core.management import execute_from_command_line
import subprocess


class CentralizedTestRunner:
    """Centralized test runner for the Aevum Health Platform"""
    
    def __init__(self):
        self.apps = [
            'authentication',
            'ai_companion', 
            'dna_profile',
            'mental_wellness',
            'smart_journal',
            'healthcare',
            'nutrition',
            'dashboard'
        ]
        
        self.test_types = [
            'api',
            'integration',
            'unit',
            'performance'
        ]
        
        self.test_results = {}
        self.total_start_time = time.time()
    
    def setup_django(self):
        """Setup Django for testing"""
        if not settings.configured:
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aevum.settings')
            django.setup()
    
    def run_app_tests(self, app_name, verbosity=2):
        """Run tests for a specific app"""
        print(f"\n{'='*60}")
        print(f"🧪 TESTING {app_name.upper()} APP")
        print(f"{'='*60}")
        
        start_time = time.time()
        
        try:
            # Run Django tests for the app
            test_command = [
                'python', 'manage.py', 'test', 
                f'tests.{app_name}',
                '--verbosity', str(verbosity),
                '--keepdb'  # Keep test database for faster subsequent runs
            ]
            
            result = subprocess.run(test_command, capture_output=True, text=True)
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                print(f"✅ {app_name.upper()} tests PASSED ({duration:.2f}s)")
                self.test_results[app_name] = {'status': 'PASSED', 'duration': duration}
            else:
                print(f"❌ {app_name.upper()} tests FAILED ({duration:.2f}s)")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                self.test_results[app_name] = {'status': 'FAILED', 'duration': duration}
                
        except Exception as e:
            duration = time.time() - start_time
            print(f"💥 {app_name.upper()} tests ERROR ({duration:.2f}s): {str(e)}")
            self.test_results[app_name] = {'status': 'ERROR', 'duration': duration}
    
    def run_type_tests(self, test_type, verbosity=2):
        """Run tests of a specific type (api, integration, unit, performance)"""
        print(f"\n{'='*60}")
        print(f"🧪 TESTING {test_type.upper()} TESTS")
        print(f"{'='*60}")
        
        start_time = time.time()
        
        try:
            test_command = [
                'python', 'manage.py', 'test', 
                f'tests.{test_type}',
                '--verbosity', str(verbosity),
                '--keepdb'
            ]
            
            result = subprocess.run(test_command, capture_output=True, text=True)
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                print(f"✅ {test_type.upper()} tests PASSED ({duration:.2f}s)")
                self.test_results[f"{test_type}_tests"] = {'status': 'PASSED', 'duration': duration}
            else:
                print(f"❌ {test_type.upper()} tests FAILED ({duration:.2f}s)")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                self.test_results[f"{test_type}_tests"] = {'status': 'FAILED', 'duration': duration}
                
        except Exception as e:
            duration = time.time() - start_time
            print(f"💥 {test_type.upper()} tests ERROR ({duration:.2f}s): {str(e)}")
            self.test_results[f"{test_type}_tests"] = {'status': 'ERROR', 'duration': duration}
    
    def run_all_tests(self, verbosity=2):
        """Run all tests"""
        print(f"\n{'='*80}")
        print("🚀 RUNNING ALL AEVUM HEALTH PLATFORM TESTS")
        print(f"{'='*80}")
        
        # Run app-specific tests
        for app in self.apps:
            self.run_app_tests(app, verbosity)
        
        # Run type-specific tests
        for test_type in self.test_types:
            self.run_type_tests(test_type, verbosity)
    
    def run_coverage_tests(self):
        """Run tests with coverage reporting"""
        print(f"\n{'='*60}")
        print("📊 RUNNING TESTS WITH COVERAGE")
        print(f"{'='*60}")
        
        try:
            # Install coverage if not available
            subprocess.run(['pip', 'install', 'coverage'], capture_output=True)
            
            # Run tests with coverage
            coverage_command = [
                'coverage', 'run', '--source', '.', 
                'manage.py', 'test', 'tests',
                '--keepdb'
            ]
            
            result = subprocess.run(coverage_command)
            
            if result.returncode == 0:
                print("✅ Coverage tests completed successfully")
                
                # Generate coverage report
                print("\n📈 COVERAGE REPORT:")
                subprocess.run(['coverage', 'report'])
                
                # Generate HTML coverage report
                subprocess.run(['coverage', 'html'])
                print("\n📄 HTML coverage report generated in htmlcov/")
                
            else:
                print("❌ Coverage tests failed")
                
        except Exception as e:
            print(f"💥 Coverage tests ERROR: {str(e)}")
    
    def print_summary(self):
        """Print test execution summary"""
        total_duration = time.time() - self.total_start_time
        
        print(f"\n{'='*80}")
        print("📋 TEST EXECUTION SUMMARY")
        print(f"{'='*80}")
        
        passed = sum(1 for result in self.test_results.values() if result['status'] == 'PASSED')
        failed = sum(1 for result in self.test_results.values() if result['status'] == 'FAILED')
        errors = sum(1 for result in self.test_results.values() if result['status'] == 'ERROR')
        
        print(f"📊 Results: {passed} PASSED, {failed} FAILED, {errors} ERRORS")
        print(f"⏱️  Total Duration: {total_duration:.2f} seconds")
        
        if self.test_results:
            print(f"\n📝 Detailed Results:")
            for test_name, result in self.test_results.items():
                status_emoji = "✅" if result['status'] == 'PASSED' else "❌" if result['status'] == 'FAILED' else "💥"
                print(f"  {status_emoji} {test_name}: {result['status']} ({result['duration']:.2f}s)")
        
        if failed == 0 and errors == 0:
            print(f"\n🎉 ALL TESTS PASSED! Platform is ready for deployment.")
        else:
            print(f"\n⚠️  Some tests failed. Please review the results above.")


def main():
    """Main test runner entry point"""
    parser = argparse.ArgumentParser(description='Aevum Health Platform Test Runner')
    parser.add_argument('--app', choices=['auth', 'ai', 'dna', 'mental', 'journal', 'health', 'nutrition', 'dashboard'], 
                       help='Run tests for specific app only')
    parser.add_argument('--type', choices=['api', 'integration', 'unit', 'performance'], 
                       help='Run specific type of tests only')
    parser.add_argument('--coverage', action='store_true', help='Run tests with coverage reporting')
    parser.add_argument('--fast', action='store_true', help='Run fast tests only (skip integration and performance)')
    parser.add_argument('--integration', action='store_true', help='Run integration tests only')
    parser.add_argument('--verbose', '-v', action='count', default=1, help='Increase verbosity')
    
    args = parser.parse_args()
    
    # Map short app names to full names
    app_mapping = {
        'auth': 'authentication',
        'ai': 'ai_companion',
        'dna': 'dna_profile',
        'mental': 'mental_wellness',
        'journal': 'smart_journal',
        'health': 'healthcare',
        'nutrition': 'nutrition',
        'dashboard': 'dashboard'
    }
    
    runner = CentralizedTestRunner()
    runner.setup_django()
    
    try:
        if args.coverage:
            runner.run_coverage_tests()
        elif args.app:
            app_name = app_mapping.get(args.app, args.app)
            runner.run_app_tests(app_name, args.verbose)
        elif args.type:
            runner.run_type_tests(args.type, args.verbose)
        elif args.integration:
            runner.run_type_tests('integration', args.verbose)
        elif args.fast:
            # Run only unit and api tests (skip integration and performance)
            runner.run_type_tests('unit', args.verbose)
            runner.run_type_tests('api', args.verbose)
            for app in runner.apps:
                runner.run_app_tests(app, args.verbose)
        else:
            runner.run_all_tests(args.verbose)
            
    finally:
        runner.print_summary()


if __name__ == '__main__':
    main() 