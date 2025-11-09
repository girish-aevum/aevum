#!/usr/bin/env python
"""
Test Migration Validation Script

This script validates that the test migration was successful by:
1. Checking that all new test files exist
2. Verifying test files can be imported
3. Ensuring Django can discover the tests
4. Running a quick test to verify functionality

Usage:
    python validate_migration.py
"""

import os
import sys
import django
import importlib
from pathlib import Path


def setup_django():
    """Setup Django environment for testing"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aevum.settings')
    django.setup()


def validate_file_structure():
    """Validate that the expected test file structure exists"""
    print("🔍 Validating file structure...")
    
    base_dir = Path(__file__).parent
    tests_dir = base_dir / 'tests'
    
    expected_files = [
        'tests/__init__.py',
        'tests/test_runner.py',
        'tests/README.md',
        
        # App directories
        'tests/authentication/__init__.py',
        'tests/authentication/test_models.py',
        'tests/authentication/test_api.py',
        
        # Test type directories
        'tests/api/__init__.py',
        'tests/integration/__init__.py',
        'tests/unit/__init__.py',
        'tests/performance/__init__.py',
        
        # Sample test files
        'tests/integration/test_user_workflows.py',
        'tests/performance/test_api_performance.py',
    ]
    
    missing_files = []
    for file_path in expected_files:
        full_path = base_dir / file_path
        if not full_path.exists():
            missing_files.append(file_path)
        else:
            print(f"  ✅ {file_path}")
    
    if missing_files:
        print(f"\n❌ Missing files:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        return False
    
    print("✅ File structure validation passed!")
    return True


def validate_imports():
    """Validate that test modules can be imported"""
    print("\n🔍 Validating test imports...")
    
    test_modules = [
        'tests',
        'tests.authentication',
        'tests.authentication.test_models',
        'tests.authentication.test_api',
        'tests.api',
        'tests.integration',
        'tests.integration.test_user_workflows',
        'tests.performance',
        'tests.performance.test_api_performance',
    ]
    
    import_errors = []
    for module in test_modules:
        try:
            importlib.import_module(module)
            print(f"  ✅ {module}")
        except ImportError as e:
            import_errors.append((module, str(e)))
            print(f"  ❌ {module}: {str(e)}")
    
    if import_errors:
        print(f"\n❌ Import errors found:")
        for module, error in import_errors:
            print(f"  - {module}: {error}")
        return False
    
    print("✅ Import validation passed!")
    return True


def validate_django_discovery():
    """Validate that Django can discover the tests"""
    print("\n🔍 Validating Django test discovery...")
    
    try:
        from django.test.utils import get_runner
        from django.conf import settings
        
        # Get the test runner
        TestRunner = get_runner(settings)
        test_runner = TestRunner(verbosity=0, interactive=False, keepdb=True)
        
        # Try to discover tests
        suite = test_runner.build_suite(['tests'])
        test_count = suite.countTestCases()
        
        print(f"  ✅ Discovered {test_count} test cases")
        
        if test_count == 0:
            print("  ⚠️  No tests discovered - this might indicate an issue")
            return False
        
        print("✅ Django test discovery passed!")
        return True
        
    except Exception as e:
        print(f"  ❌ Django test discovery failed: {str(e)}")
        return False


def run_sample_test():
    """Run a simple test to verify functionality"""
    print("\n🔍 Running sample test...")
    
    try:
        from django.test import TestCase
        from django.contrib.auth.models import User
        
        # Create a simple test case
        class ValidationTest(TestCase):
            def test_user_creation(self):
                user = User.objects.create_user(
                    username='testuser',
                    email='test@example.com',
                    password='testpass123'
                )
                self.assertIsNotNone(user)
                self.assertEqual(user.username, 'testuser')
        
        # Run the test
        import unittest
        suite = unittest.TestLoader().loadTestsFromTestCase(ValidationTest)
        runner = unittest.TextTestRunner(verbosity=0)
        result = runner.run(suite)
        
        if result.wasSuccessful():
            print("  ✅ Sample test passed!")
            return True
        else:
            print(f"  ❌ Sample test failed: {len(result.failures)} failures, {len(result.errors)} errors")
            return False
            
    except Exception as e:
        print(f"  ❌ Sample test error: {str(e)}")
        return False


def check_old_files():
    """Check if old test files still exist"""
    print("\n🔍 Checking for old test files...")
    
    base_dir = Path(__file__).parent
    old_test_files = [
        'authentication/tests.py',
        'dashboard/tests.py',
        'dashboard/test_dashboard_endpoints.py',
        'healthcare/tests.py',
        'nutrition/tests.py',
        'smart_journal/tests.py',
        'ai_companion/tests.py',
        'dna_profile/tests.py',
        'dna_profile/test_dna_order.py',
        'mental_wellness/tests.py',
        'mental_wellness/test_mood_endpoints.py',
    ]
    
    existing_old_files = []
    for file_path in old_test_files:
        full_path = base_dir / file_path
        if full_path.exists():
            existing_old_files.append(file_path)
    
    if existing_old_files:
        print("  ⚠️  Old test files still exist:")
        for file_path in existing_old_files:
            print(f"    - {file_path}")
        print("  💡 Consider running: python migrate_tests.py --cleanup")
    else:
        print("  ✅ No old test files found (already cleaned up)")
    
    return len(existing_old_files) == 0


def main():
    """Main validation function"""
    print("🧪 Aevum Health Platform - Test Migration Validation")
    print("=" * 60)
    
    # Setup Django
    setup_django()
    
    # Run validations
    validations = [
        ("File Structure", validate_file_structure),
        ("Module Imports", validate_imports),
        ("Django Test Discovery", validate_django_discovery),
        ("Sample Test Execution", run_sample_test),
    ]
    
    results = []
    for name, validation_func in validations:
        try:
            result = validation_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} validation failed with error: {str(e)}")
            results.append((name, False))
    
    # Check old files (informational)
    old_files_cleaned = check_old_files()
    
    # Print summary
    print("\n" + "=" * 60)
    print("📋 VALIDATION SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {status}: {name}")
    
    print(f"\nResults: {passed}/{total} validations passed")
    
    if passed == total:
        print("\n🎉 All validations passed! Test migration is successful.")
        print("\nNext steps:")
        print("1. Run the full test suite: python tests/test_runner.py")
        print("2. Update CI/CD configuration to use new test structure")
        if not old_files_cleaned:
            print("3. Clean up old test files: python migrate_tests.py --cleanup")
    else:
        print("\n⚠️  Some validations failed. Please review the issues above.")
        print("Consider re-running the migration or fixing the reported issues.")
    
    return passed == total


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 