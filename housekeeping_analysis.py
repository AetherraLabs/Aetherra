#!/usr/bin/env python3
"""
Comprehensive Housekeeping Analysis for Aetherra Project
Identifies files to consolidate, remove, or preserve.
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict

class ProjectHousekeeping:
    def __init__(self, root_path):
        self.root = Path(root_path)
        self.analysis = {
            'total_files': 0,
            'by_extension': defaultdict(int),
            'by_directory': defaultdict(int),
            'duplicates': [],
            'test_files': [],
            'documentation_files': [],
            'backup_files': [],
            'temp_files': [],
            'important_files': [],
            'consolidation_candidates': []
        }
        
    def analyze_project(self):
        """Analyze the entire project structure"""
        print("🔍 Analyzing project structure...")
        
        for file_path in self.root.rglob('*'):
            if file_path.is_file():
                self.analysis['total_files'] += 1
                self.analyze_file(file_path)
                
        self.identify_duplicates()
        self.categorize_files()
        self.generate_consolidation_plan()
        
    def analyze_file(self, file_path):
        """Analyze individual file"""
        relative_path = file_path.relative_to(self.root)
        extension = file_path.suffix.lower()
        directory = str(relative_path.parent)
        
        # Count by extension and directory
        self.analysis['by_extension'][extension] += 1
        self.analysis['by_directory'][directory] += 1
        
        # Categorize files
        file_str = str(relative_path).lower()
        
        # Test files
        if any(keyword in file_str for keyword in ['test_', 'test\\', 'tests\\', '_test.py', 'testing\\']):
            self.analysis['test_files'].append(str(relative_path))
            
        # Documentation files
        if extension in ['.md', '.txt', '.rst'] or 'doc' in file_str:
            self.analysis['documentation_files'].append(str(relative_path))
            
        # Backup files
        if any(keyword in file_str for keyword in ['backup', '.bak', '.old', 'archive']):
            self.analysis['backup_files'].append(str(relative_path))
            
        # Temp files
        if any(keyword in file_str for keyword in ['.tmp', '.temp', '__pycache__', '.pyc', '.log']):
            self.analysis['temp_files'].append(str(relative_path))
            
        # Important files (preserve these)
        if any(keyword in file_str for keyword in [
            'launcher', 'main.py', 'run_', 'aetherra_', 'lyrixa\\',
            'core\\', 'src\\aetherra', 'tools\\', 'sdk\\'
        ]) and not any(test_keyword in file_str for test_keyword in ['test_', 'demo_']):
            self.analysis['important_files'].append(str(relative_path))
            
    def identify_duplicates(self):
        """Identify potential duplicate files"""
        print("🔍 Identifying duplicates...")
        
        # Group files by name (ignoring path)
        files_by_name = defaultdict(list)
        
        for file_path in self.root.rglob('*.py'):
            relative_path = file_path.relative_to(self.root)
            files_by_name[file_path.name].append(str(relative_path))
            
        # Find duplicates
        for filename, paths in files_by_name.items():
            if len(paths) > 1:
                # Skip if one is clearly a test version
                non_test_paths = [p for p in paths if 'test' not in p.lower()]
                if len(non_test_paths) > 1:
                    self.analysis['duplicates'].append({
                        'filename': filename,
                        'paths': paths,
                        'count': len(paths)
                    })
                    
    def categorize_files(self):
        """Categorize files for consolidation"""
        print("📋 Categorizing files...")
        
        # Test file consolidation
        test_dirs = set()
        for test_file in self.analysis['test_files']:
            test_dir = str(Path(test_file).parent)
            test_dirs.add(test_dir)
            
        if len(test_dirs) > 3:  # Multiple test directories
            self.analysis['consolidation_candidates'].append({
                'type': 'test_directories',
                'current_dirs': list(test_dirs),
                'recommended_dirs': ['tests/unit', 'tests/integration', 'testing/verification'],
                'file_count': len(self.analysis['test_files'])
            })
            
        # Documentation consolidation
        doc_dirs = set()
        for doc_file in self.analysis['documentation_files']:
            doc_dir = str(Path(doc_file).parent)
            doc_dirs.add(doc_dir)
            
        if len(doc_dirs) > 2:
            self.analysis['consolidation_candidates'].append({
                'type': 'documentation_directories',
                'current_dirs': list(doc_dirs),
                'recommended_dirs': ['docs', 'documentation'],
                'file_count': len(self.analysis['documentation_files'])
            })
            
    def generate_consolidation_plan(self):
        """Generate a consolidation plan"""
        print("📝 Generating consolidation plan...")
        
        plan = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_files': self.analysis['total_files'],
                'test_files': len(self.analysis['test_files']),
                'documentation_files': len(self.analysis['documentation_files']),
                'backup_files': len(self.analysis['backup_files']),
                'temp_files': len(self.analysis['temp_files']),
                'duplicates': len(self.analysis['duplicates'])
            },
            'recommendations': self.generate_recommendations()
        }
        
        return plan
        
    def generate_recommendations(self):
        """Generate specific recommendations"""
        recommendations = []
        
        # Remove temp files
        if self.analysis['temp_files']:
            recommendations.append({
                'action': 'remove',
                'category': 'temporary_files',
                'files': self.analysis['temp_files'][:10],  # Show first 10
                'total_count': len(self.analysis['temp_files']),
                'priority': 'high',
                'safe': True
            })
            
        # Consolidate test files
        if len(self.analysis['test_files']) > 50:
            recommendations.append({
                'action': 'consolidate',
                'category': 'test_files',
                'target_structure': {
                    'tests/unit/': 'Unit tests',
                    'tests/integration/': 'Integration tests',
                    'testing/verification/': 'Verification scripts'
                },
                'file_count': len(self.analysis['test_files']),
                'priority': 'medium',
                'safe': True
            })
            
        # Archive old documentation
        old_docs = [f for f in self.analysis['documentation_files'] 
                   if any(keyword in f.lower() for keyword in ['complete', 'fixes', 'summary'])]
        if len(old_docs) > 20:
            recommendations.append({
                'action': 'archive',
                'category': 'old_documentation',
                'files': old_docs[:5],  # Show first 5
                'total_count': len(old_docs),
                'target': 'archive/documentation/',
                'priority': 'low',
                'safe': True
            })
            
        # Remove duplicates
        if self.analysis['duplicates']:
            recommendations.append({
                'action': 'deduplicate',
                'category': 'duplicate_files',
                'duplicates': self.analysis['duplicates'][:5],  # Show first 5
                'total_count': len(self.analysis['duplicates']),
                'priority': 'medium',
                'safe': False  # Requires manual review
            })
            
        return recommendations
        
    def save_analysis(self, output_file='housekeeping_analysis.json'):
        """Save analysis to file"""
        output_path = self.root / output_file
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.analysis, f, indent=2, ensure_ascii=False)
            
        print(f"📄 Analysis saved to: {output_path}")
        
    def print_summary(self):
        """Print analysis summary"""
        print("\n" + "="*80)
        print("🏠 AETHERRA PROJECT HOUSEKEEPING ANALYSIS")
        print("="*80)
        
        print(f"\n📊 PROJECT STATISTICS:")
        print(f"   Total files: {self.analysis['total_files']:,}")
        print(f"   Test files: {len(self.analysis['test_files']):,}")
        print(f"   Documentation files: {len(self.analysis['documentation_files']):,}")
        print(f"   Backup files: {len(self.analysis['backup_files']):,}")
        print(f"   Temporary files: {len(self.analysis['temp_files']):,}")
        print(f"   Important files: {len(self.analysis['important_files']):,}")
        print(f"   Potential duplicates: {len(self.analysis['duplicates']):,}")
        
        print(f"\n📁 TOP FILE TYPES:")
        sorted_extensions = sorted(self.analysis['by_extension'].items(), 
                                 key=lambda x: x[1], reverse=True)[:10]
        for ext, count in sorted_extensions:
            ext_display = ext if ext else '(no extension)'
            print(f"   {ext_display}: {count:,}")
            
        print(f"\n📂 TOP DIRECTORIES:")
        sorted_dirs = sorted(self.analysis['by_directory'].items(), 
                           key=lambda x: x[1], reverse=True)[:10]
        for dir_name, count in sorted_dirs:
            dir_display = dir_name if dir_name != '.' else '(root)'
            print(f"   {dir_display}: {count:,}")
            
        if self.analysis['duplicates']:
            print(f"\n🔄 SAMPLE DUPLICATES:")
            for i, dup in enumerate(self.analysis['duplicates'][:5]):
                print(f"   {i+1}. {dup['filename']} ({dup['count']} copies)")
                for path in dup['paths'][:3]:
                    print(f"      - {path}")
                if len(dup['paths']) > 3:
                    print(f"      - ... and {len(dup['paths'])-3} more")
                    
        print("\n" + "="*80)

def main():
    """Main housekeeping analysis"""
    root_path = Path.cwd()
    
    print("🏠 Starting Aetherra Project Housekeeping Analysis...")
    print(f"📁 Analyzing: {root_path}")
    
    hk = ProjectHousekeeping(root_path)
    hk.analyze_project()
    
    # Save analysis
    hk.save_analysis()
    
    # Print summary
    hk.print_summary()
    
    # Generate consolidation plan
    plan = hk.generate_consolidation_plan()
    
    # Save plan
    plan_file = root_path / 'consolidation_plan.json'
    with open(plan_file, 'w', encoding='utf-8') as f:
        json.dump(plan, f, indent=2, ensure_ascii=False)
        
    print(f"\n📋 Consolidation plan saved to: {plan_file}")
    print("\n✅ Analysis complete! Review the plan before proceeding with housekeeping.")

if __name__ == "__main__":
    main()
