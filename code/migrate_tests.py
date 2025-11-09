#!/usr/bin/env python
"""
Test Migration Script

This script helps migrate from the old individual app test structure
to the new centralized test structure.

Usage:
    python migrate_tests.py --dry-run    # Preview changes
    python migrate_tests.py --migrate    # Perform migration
    python migrate_tests.py --cleanup    # Remove old test files
"""

import os
import sys
import shutil
import argparse
from pathlib import Path


class TestMigrator:
    """Handles migration of test files to centralized structure"""
    
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.base_dir = Path(__file__).parent
        self.tests_dir = self.base_dir / 'tests'
        
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
        
        self.migration_map = {
            # Old file -> New location mapping
            'authentication/tests.py': 'tests/authentication/test_models.py',
            'dashboard/tests.py': 'tests/dashboard/test_models.py',
            'dashboard/test_dashboard_endpoints.py': 'tests/api/test_dashboard_endpoints.py',
            'healthcare/tests.py': 'tests/healthcare/test_models.py',
            'nutrition/tests.py': 'tests/nutrition/test_models.py',
            'smart_journal/tests.py': 'tests/smart_journal/test_models.py',
            'ai_companion/tests.py': 'tests/ai_companion/test_models.py',
            'dna_profile/tests.py': 'tests/dna_profile/test_models.py',
            'dna_profile/test_dna_order.py': 'tests/api/test_dna_order.py',
            'mental_wellness/tests.py': 'tests/mental_wellness/test_models.py',
            'mental_wellness/test_mood_endpoints.py': 'tests/api/test_mood_endpoints.py',
        }
        
        self.results = {
            'copied': [],
            'skipped': [],
            'errors': []
        }
    
    def log(self, message, level='INFO'):
        """Log a message with appropriate formatting"""
        prefix = "[DRY RUN] " if self.dry_run else ""
        print(f"{prefix}{level}: {message}")
    
    def ensure_directory(self, file_path):
        """Ensure the directory for a file path exists"""
        directory = os.path.dirname(file_path)
        if not self.dry_run and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            self.log(f"Created directory: {directory}")
    
    def copy_test_file(self, source, destination):
        """Copy a test file from source to destination"""
        source_path = self.base_dir / source
        dest_path = self.base_dir / destination
        
        if not source_path.exists():
            self.log(f"Source file not found: {source}", 'WARNING')
            self.results['skipped'].append(source)
            return False
        
        if dest_path.exists():
            self.log(f"Destination already exists: {destination}", 'WARNING')
            self.results['skipped'].append(source)
            return False
        
        try:
            self.ensure_directory(str(dest_path))
            
            if not self.dry_run:
                shutil.copy2(str(source_path), str(dest_path))
            
            self.log(f"Copied: {source} -> {destination}")
            self.results['copied'].append((source, destination))
            return True
            
        except Exception as e:
            self.log(f"Error copying {source}: {str(e)}", 'ERROR')
            self.results['errors'].append((source, str(e)))
            return False
    
    def migrate_tests(self):
        """Migrate all test files to the new structure"""
        self.log("Starting test migration...")
        self.log(f"Base directory: {self.base_dir}")
        self.log(f"Tests directory: {self.tests_dir}")
        
        # Ensure tests directory exists
        if not self.dry_run and not self.tests_dir.exists():
            self.tests_dir.mkdir(parents=True, exist_ok=True)
            self.log(f"Created tests directory: {self.tests_dir}")
        
        # Copy files according to migration map
        for source, destination in self.migration_map.items():
            self.copy_test_file(source, destination)
        
        # Look for additional test files that might have been missed
        self.discover_additional_tests()
        
        self.print_summary()
    
    def discover_additional_tests(self):
        """Discover any additional test files that weren't in the migration map"""
        self.log("Discovering additional test files...")
        
        for app in self.apps:
            app_dir = self.base_dir / app
            if not app_dir.exists():
                continue
            
            # Look for test files
            test_files = []
            test_files.extend(app_dir.glob('test_*.py'))
            test_files.extend(app_dir.glob('*_test.py'))
            test_files.extend(app_dir.glob('**/test_*.py'))
            test_files.extend(app_dir.glob('**/*_test.py'))
            
            for test_file in test_files:
                relative_path = str(test_file.relative_to(self.base_dir))
                
                # Skip if already in migration map
                if relative_path in self.migration_map:
                    continue
                
                # Determine destination based on file name and content
                if 'endpoint' in test_file.name or 'api' in test_file.name:
                    destination = f"tests/api/{test_file.name}"
                elif 'integration' in test_file.name:
                    destination = f"tests/integration/{test_file.name}"
                elif 'performance' in test_file.name:
                    destination = f"tests/performance/{test_file.name}"
                else:
                    destination = f"tests/{app}/{test_file.name}"
                
                self.log(f"Discovered: {relative_path} -> {destination}")
                self.copy_test_file(relative_path, destination)
    
    def cleanup_old_tests(self):
        """Remove old test files after successful migration"""
        self.log("Cleaning up old test files...")
        
        if self.dry_run:
            self.log("Would remove the following files:")
            for source, _ in self.migration_map.items():
                source_path = self.base_dir / source
                if source_path.exists():
                    self.log(f"  - {source}")
            return
        
        # Only cleanup if migration was successful
        if self.results['errors']:
            self.log("Skipping cleanup due to migration errors", 'WARNING')
            return
        
        for source, _ in self.migration_map.items():
            source_path = self.base_dir / source
            if source_path.exists():
                try:
                    source_path.unlink()
                    self.log(f"Removed: {source}")
                except Exception as e:
                    self.log(f"Error removing {source}: {str(e)}", 'ERROR')
    
    def print_summary(self):
        """Print migration summary"""
        self.log("\n" + "="*60)
        self.log("MIGRATION SUMMARY")
        self.log("="*60)
        
        self.log(f"Files copied: {len(self.results['copied'])}")
        for source, dest in self.results['copied']:
            self.log(f"  ✅ {source} -> {dest}")
        
        if self.results['skipped']:
            self.log(f"\nFiles skipped: {len(self.results['skipped'])}")
            for source in self.results['skipped']:
                self.log(f"  ⏭️  {source}")
        
        if self.results['errors']:
            self.log(f"\nErrors: {len(self.results['errors'])}")
            for source, error in self.results['errors']:
                self.log(f"  ❌ {source}: {error}")
        
        self.log(f"\nTotal processed: {len(self.migration_map)} files")
        
        if not self.dry_run and not self.results['errors']:
            self.log("\n🎉 Migration completed successfully!")
            self.log("Next steps:")
            self.log("1. Run tests to verify everything works:")
            self.log("   python tests/test_runner.py")
            self.log("2. Update your CI/CD scripts to use the new test structure")
            self.log("3. Clean up old test files:")
            self.log("   python migrate_tests.py --cleanup")
        elif self.dry_run:
            self.log("\n👀 This was a dry run. Use --migrate to perform actual migration.")


def main():
    """Main migration script entry point"""
    parser = argparse.ArgumentParser(description='Migrate tests to centralized structure')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Preview changes without making them')
    parser.add_argument('--migrate', action='store_true', 
                       help='Perform the migration')
    parser.add_argument('--cleanup', action='store_true', 
                       help='Remove old test files after migration')
    
    args = parser.parse_args()
    
    if not any([args.dry_run, args.migrate, args.cleanup]):
        print("Please specify one of: --dry-run, --migrate, --cleanup")
        parser.print_help()
        return
    
    migrator = TestMigrator(dry_run=args.dry_run or not args.migrate)
    
    if args.cleanup:
        migrator.cleanup_old_tests()
    else:
        migrator.migrate_tests()


if __name__ == '__main__':
    main() 