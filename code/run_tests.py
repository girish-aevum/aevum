#!/usr/bin/env python
"""
Comprehensive Test Runner for Aevum Health Platform
Runs all tests across all apps with detailed reporting and coverage analysis
"""

import os
import sys
import django
import time
from django.conf import settings
from django.test.utils import get_runner
from django.core.management import execute_from_command_line
import subprocess


class AevumTestRunner:
    """Custom test runner for Aevum Health Platform"""
    
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
        
        self.test_results = {}
        self.total_start_time = time.time()
    
    def setup_django(self):
        """Setup Django for testing"""
        if not settings.configured:
            # Import the project settings
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aevum.settings')
            django.setup()
    
    def run_app_tests(self, app_name, verbosity=2):
        """Run tests for a specific app"""
        print(f"\n{'='*60}")
        print(f"🧪 TESTING {app_name.upper()} APP")
        print(f"{'='*60}")
        
        start_time = time.time()
        
        try:
            # Run Django tests
            TestRunner = get_runner(settings)
            test_runner = TestRunner(verbosity=verbosity, interactive=False)
            
            # Run tests for the specific app
            failures = test_runner.run_tests([app_name])
            
            end_time = time.time()
            duration = end_time - start_time
            
            self.test_results[app_name] = {
                'success': failures == 0,
                'failures': failures,
                'duration': duration
            }
            
            if failures == 0:
                print(f"✅ {app_name} tests PASSED in {duration:.2f}s")
            else:
                print(f"❌ {app_name} tests FAILED ({failures} failures) in {duration:.2f}s")
                
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            
            self.test_results[app_name] = {
                'success': False,
                'failures': 1,
                'duration': duration,
                'error': str(e)
            }
            print(f"💥 {app_name} tests ERROR: {str(e)}")
    
    def run_all_tests(self, verbosity=2):
        """Run tests for all apps"""
        print("🚀 Starting Aevum Health Platform Test Suite")
        print(f"📊 Testing {len(self.apps)} applications")
        
        for app in self.apps:
            self.run_app_tests(app, verbosity)
        
        self.print_summary()
    
    def run_specific_tests(self, apps, verbosity=2):
        """Run tests for specific apps"""
        print(f"🎯 Running tests for specific apps: {', '.join(apps)}")
        
        for app in apps:
            if app in self.apps:
                self.run_app_tests(app, verbosity)
            else:
                print(f"⚠️  Warning: App '{app}' not found in available apps")
        
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        total_end_time = time.time()
        total_duration = total_end_time - self.total_start_time
        
        print(f"\n{'='*60}")
        print("📋 TEST SUMMARY")
        print(f"{'='*60}")
        
        passed_apps = []
        failed_apps = []
        total_failures = 0
        
        for app, result in self.test_results.items():
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            duration = result['duration']
            failures = result.get('failures', 0)
            
            print(f"{app:<20} {status:<10} {duration:>8.2f}s", end="")
            
            if not result['success']:
                if 'error' in result:
                    print(f" (ERROR: {result['error'][:30]}...)")
                else:
                    print(f" ({failures} failures)")
                failed_apps.append(app)
                total_failures += failures
            else:
                print()
                passed_apps.append(app)
        
        print(f"\n{'='*60}")
        print(f"📊 FINAL RESULTS")
        print(f"{'='*60}")
        print(f"Total Apps Tested: {len(self.test_results)}")
        print(f"Passed: {len(passed_apps)}")
        print(f"Failed: {len(failed_apps)}")
        print(f"Total Duration: {total_duration:.2f}s")
        print(f"Total Failures: {total_failures}")
        
        if failed_apps:
            print(f"\n❌ Failed Apps: {', '.join(failed_apps)}")
        
        if passed_apps:
            print(f"✅ Passed Apps: {', '.join(passed_apps)}")
        
        # Overall status
        if len(failed_apps) == 0:
            print(f"\n🎉 ALL TESTS PASSED! 🎉")
            return True
        else:
            print(f"\n💥 {len(failed_apps)} APP(S) FAILED")
            return False
    
    def run_coverage_analysis(self):
        """Run coverage analysis"""
        print(f"\n{'='*60}")
        print("📈 RUNNING COVERAGE ANALYSIS")
        print(f"{'='*60}")
        
        try:
            # Install coverage if not available
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'coverage'], 
                         capture_output=True, check=False)
            
            # Run tests with coverage
            coverage_cmd = [
                'coverage', 'run', '--source=.', 
                'manage.py', 'test'
            ] + self.apps
            
            result = subprocess.run(coverage_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Coverage analysis completed")
                
                # Generate coverage report
                report_result = subprocess.run(['coverage', 'report'], 
                                             capture_output=True, text=True)
                if report_result.returncode == 0:
                    print("\n📊 COVERAGE REPORT:")
                    print(report_result.stdout)
                
                # Generate HTML coverage report
                html_result = subprocess.run(['coverage', 'html'], 
                                           capture_output=True, text=True)
                if html_result.returncode == 0:
                    print("📄 HTML coverage report generated: htmlcov/index.html")
            else:
                print(f"❌ Coverage analysis failed: {result.stderr}")
                
        except FileNotFoundError:
            print("⚠️  Coverage tool not available. Install with: pip install coverage")
        except Exception as e:
            print(f"❌ Coverage analysis error: {str(e)}")


def main():
    """Main test runner function"""
    # Parse command line arguments
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Comprehensive test runner for Aevum Health Platform'
    )
    parser.add_argument(
        '--apps', 
        nargs='+', 
        help='Specific apps to test (default: all apps)'
    )
    parser.add_argument(
        '--verbosity', 
        type=int, 
        default=2, 
        choices=[0, 1, 2, 3],
        help='Test verbosity level (default: 2)'
    )
    parser.add_argument(
        '--coverage', 
        action='store_true',
        help='Run coverage analysis'
    )
    parser.add_argument(
        '--fast', 
        action='store_true',
        help='Run tests with minimal verbosity for faster execution'
    )
    
    args = parser.parse_args()
    
    # Adjust verbosity for fast mode
    if args.fast:
        args.verbosity = 1
    
    # Initialize test runner
    runner = AevumTestRunner()
    runner.setup_django()
    
    # Run tests
    if args.apps:
        success = runner.run_specific_tests(args.apps, args.verbosity)
    else:
        success = runner.run_all_tests(args.verbosity)
    
    # Run coverage analysis if requested
    if args.coverage:
        runner.run_coverage_analysis()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()


# Additional utility functions for CI/CD integration

def run_quick_tests():
    """Run a quick subset of tests for rapid feedback"""
    runner = AevumTestRunner()
    runner.setup_django()
    
    # Run only critical tests
    critical_apps = ['authentication', 'ai_companion']
    return runner.run_specific_tests(critical_apps, verbosity=1)


def run_integration_tests():
    """Run integration tests across all apps"""
    runner = AevumTestRunner()
    runner.setup_django()
    
    print("🔗 Running Integration Tests")
    
    # Run all tests with focus on integration
    return runner.run_all_tests(verbosity=2)


def validate_test_environment():
    """Validate that the test environment is properly set up"""
    print("🔍 Validating Test Environment")
    
    required_packages = [
        'django',
        'djangorestframework', 
        'djangorestframework-simplejwt',
        'pillow'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} - OK")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    print("✅ Test environment validation passed")
    return True


# Example usage:
"""
# Run all tests
python run_tests.py

# Run specific apps
python run_tests.py --apps authentication ai_companion

# Run with coverage
python run_tests.py --coverage

# Fast mode (minimal output)
python run_tests.py --fast

# Run specific tests with high verbosity
python run_tests.py --apps dna_profile --verbosity 3
""" 