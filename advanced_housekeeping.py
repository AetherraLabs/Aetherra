#!/usr/bin/env python3
"""
Advanced Project Housekeeping for Aetherra
Safely consolidates, archives, and removes unnecessary files while preserving important functionality.
"""

import json
import shutil
from pathlib import Path
from datetime import datetime

class AetherraAdvancedHousekeeping:
    def __init__(self, root_path):
        self.root = Path(root_path)
        self.backup_root = self.root / "backups" / f"housekeeping_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.operations_log = []
        
        # Critical directories and files to preserve
        self.preserve_patterns = [
            'lyrixa/',
            'src/aetherra/',
            'core/',
            'Aetherra/',
            'tools/',
            'sdk/',
            'plugins/',
            'launchers/',
            'requirements.txt',
            'README.md',
            'LICENSE',
            'index.html',
            'script.js',
            'styles.css',
            'manifest.json',
            'sw.js',
            '.env',
            '.gitignore',
            'aetherra_launcher.py',
            'run_aetherra.py'
        ]
        
        # Safe to remove patterns
        self.remove_patterns = [
            '__pycache__/',
            '*.pyc',
            '*.log',
            '*.tmp',
            '.pytest_cache/',
            '.mypy_cache/',
            'test_*.db',
            'test_runtime_fresh.db',
            'test_confidence.db',
            'test_memory.db'
        ]
        
    def create_backup(self):
        """Create a full backup before starting"""
        print("📦 Creating selective backup before housekeeping...")
        self.backup_root.mkdir(parents=True, exist_ok=True)
        
        backup_log = {
            'timestamp': datetime.now().isoformat(),
            'backup_location': str(self.backup_root),
            'operation': 'pre_housekeeping_backup'
        }
        
        # Only backup important files, not the massive amount of test files
        important_items = [
            'lyrixa/',
            'src/',
            'core/',
            'Aetherra/',
            'tools/',
            'sdk/',
            'plugins/',
            'launchers/',
            'requirements.txt',
            'README.md',
            'LICENSE',
            'index.html',
            'script.js',
            'styles.css'
        ]
        
        for item in important_items:
            source = self.root / item
            if source.exists():
                target = self.backup_root / item
                if source.is_file():
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, target)
                else:
                    shutil.copytree(source, target, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '*.log'))
                print(f"   ✅ Backed up: {item}")
                
        # Save backup log
        with open(self.backup_root / 'backup_log.json', 'w') as f:
            json.dump(backup_log, f, indent=2)
            
        print(f"✅ Backup created at: {self.backup_root}")
        
    def clean_temporary_files(self):
        """Remove temporary and cache files"""
        print("\n🧹 Cleaning temporary files...")
        removed_count = 0
        
        for pattern in self.remove_patterns:
            if pattern.endswith('/'):
                # Directory pattern
                for path in self.root.rglob(pattern.rstrip('/')):
                    if path.is_dir():
                        try:
                            shutil.rmtree(path)
                            removed_count += 1
                            self.log_operation('remove_directory', str(path.relative_to(self.root)))
                            print(f"   🗑️  Removed directory: {path.relative_to(self.root)}")
                        except Exception as e:
                            print(f"   ⚠️  Could not remove {path}: {e}")
            else:
                # File pattern
                for path in self.root.rglob(pattern):
                    if path.is_file():
                        try:
                            path.unlink()
                            removed_count += 1
                            self.log_operation('remove_file', str(path.relative_to(self.root)))
                        except Exception as e:
                            print(f"   ⚠️  Could not remove {path}: {e}")
                            
        print(f"✅ Removed {removed_count} temporary files/directories")
        
    def archive_old_documentation(self):
        """Archive old documentation files"""
        print("\n📚 Archiving old documentation...")
        
        archive_dir = self.root / "archive" / "documentation"
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Patterns for old documentation
        old_doc_patterns = [
            '*_COMPLETE.md',
            '*_FIXES.md',
            '*_SUMMARY.md',
            '*_REPORT.md',
            '*IMPLEMENTATION*.md',
            'PHASE*_*.md'
        ]
        
        archived_count = 0
        for pattern in old_doc_patterns:
            for doc_file in self.root.glob(pattern):
                if doc_file.is_file() and doc_file.parent == self.root:
                    try:
                        target = archive_dir / doc_file.name
                        shutil.move(str(doc_file), str(target))
                        archived_count += 1
                        self.log_operation('archive_documentation', str(doc_file.relative_to(self.root)))
                        print(f"   📦 Archived: {doc_file.name}")
                    except Exception as e:
                        print(f"   ⚠️  Could not archive {doc_file.name}: {e}")
                        
        print(f"✅ Archived {archived_count} documentation files")
        
    def should_preserve_file(self, file_path):
        """Check if a file should be preserved"""
        relative_path = str(file_path.relative_to(self.root))
        
        for pattern in self.preserve_patterns:
            if relative_path.startswith(pattern) or pattern in relative_path:
                return True
                
        return False
        
    def log_operation(self, operation_type, details):
        """Log housekeeping operations"""
        self.operations_log.append({
            'timestamp': datetime.now().isoformat(),
            'operation': operation_type,
            'details': details
        })
        
    def save_operations_log(self):
        """Save operations log"""
        log_file = self.root / 'housekeeping_operations.json'
        with open(log_file, 'w') as f:
            json.dump(self.operations_log, f, indent=2)
        print(f"\n📝 Operations log saved to: {log_file}")
        
    def verify_important_files(self):
        """Verify that important files are still intact"""
        print("\n🔍 Verifying important files...")
        
        critical_files = [
            'lyrixa/__init__.py',
            'lyrixa/conversation_manager.py',
            'lyrixa/prompt_engine.py',
            'src/aetherra/core/ai/multi_llm_manager.py',
            'requirements.txt',
            'README.md'
        ]
        
        all_good = True
        for file_path in critical_files:
            full_path = self.root / file_path
            if full_path.exists():
                print(f"   ✅ {file_path}")
            else:
                print(f"   ❌ MISSING: {file_path}")
                all_good = False
                
        if all_good:
            print("✅ All critical files verified")
        else:
            print("⚠️  Some critical files are missing!")
            
        return all_good
        
    def get_final_stats(self):
        """Get final statistics"""
        print("\n📊 Final Statistics:")
        
        try:
            # Count remaining files
            total_files = sum(1 for _ in self.root.rglob('*') if _.is_file())
            py_files = len(list(self.root.rglob('*.py')))
            test_files = len(list(self.root.rglob('test_*.py'))) + len(list(self.root.rglob('*_test.py')))
            
            print(f"   Total files: {total_files:,}")
            print(f"   Python files: {py_files:,}")
            print(f"   Test files: {test_files:,}")
            print(f"   Operations performed: {len(self.operations_log)}")
            
        except Exception as e:
            print(f"   Could not get final statistics: {e}")
            
    def run_housekeeping(self):
        """Run complete housekeeping process"""
        print("🏠 Starting Aetherra Advanced Project Housekeeping")
        print("=" * 60)
        
        try:
            # Step 1: Create backup
            self.create_backup()
            
            # Step 2: Clean temporary files
            self.clean_temporary_files()
            
            # Step 3: Archive old documentation
            self.archive_old_documentation()
            
            # Step 4: Verify important files
            if not self.verify_important_files():
                print("\n⚠️  CRITICAL: Some important files are missing!")
                print("    Please check the backup and restore if necessary.")
                return False
                
            # Step 5: Save operations log
            self.save_operations_log()
            
            # Step 6: Final statistics
            self.get_final_stats()
            
            print("\n" + "=" * 60)
            print("✅ Housekeeping completed successfully!")
            print(f"📦 Backup location: {self.backup_root}")
            print("🔍 Review the operations log for details.")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Housekeeping failed: {e}")
            print(f"📦 Backup available at: {self.backup_root}")
            return False

def main():
    """Main housekeeping function"""
    root_path = Path.cwd()
    
    print("🏠 Aetherra Advanced Project Housekeeping Tool")
    print(f"📁 Working directory: {root_path}")
    print("⚠️  Starting automated housekeeping process...")
    print()
        
    # Run housekeeping
    hk = AetherraAdvancedHousekeeping(root_path)
    success = hk.run_housekeeping()
    
    if success:
        print("\n🎉 Project housekeeping completed successfully!")
    else:
        print("\n⚠️  Housekeeping completed with issues. Check the logs.")

if __name__ == "__main__":
    main()
