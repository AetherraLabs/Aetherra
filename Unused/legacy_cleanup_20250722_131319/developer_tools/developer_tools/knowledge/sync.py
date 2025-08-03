"""
Knowledge Base Sync - Auto-sync documentation to memory for enhanced retrieval.

This module provides automatic synchronization between project documentation
and the memory system, enabling seamless access to knowledge during development.
"""

import json
import hashlib
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import threading
import re


@dataclass
class DocumentInfo:
    """Information about a synchronized document."""
    doc_path: str
    memory_key: str
    last_modified: str
    content_hash: str
    doc_type: str  # 'markdown', 'text', 'code', 'json'
    tags: List[str]
    metadata: Dict[str, Any]


@dataclass
class SyncStats:
    """Statistics for sync operations."""
    total_docs: int
    synced_docs: int
    failed_docs: int
    updated_docs: int
    new_docs: int
    sync_time: float
    last_sync: str


class KnowledgeBaseSync:
    """Automatic synchronization system for documentation and knowledge base."""

    def __init__(self, memory_store_path: str = "memory_store.json",
                 sync_dir: str = "data/kb_sync"):
        """Initialize the knowledge base sync system.

        Args:
            memory_store_path: Path to the memory store file
            sync_dir: Directory for sync configuration and metadata
        """
        self.memory_store_path = Path(memory_store_path)
        self.sync_dir = Path(sync_dir)
        self.sync_dir.mkdir(parents=True, exist_ok=True)

        # Configuration files
        self.config_file = self.sync_dir / "sync_config.json"
        self.registry_file = self.sync_dir / "document_registry.json"
        self.stats_file = self.sync_dir / "sync_stats.json"

        # Sync configuration
        self.sync_config = self._load_sync_config()
        self.document_registry: Dict[str, DocumentInfo] = self._load_document_registry()

        # Auto-sync
        self.auto_sync_enabled = False
        self.sync_thread: Optional[threading.Thread] = None

        # Default sync patterns
        self.default_patterns = {
            'include': [
                '*.md', '*.txt', '*.rst', '*.asciidoc',
                '*.py', '*.js', '*.ts', '*.json', '*.yaml', '*.yml',
                'README*', 'CHANGELOG*', 'LICENSE*', 'CONTRIBUTING*'
            ],
            'exclude': [
                '*.pyc', '*.pyo', '*.pyd', '__pycache__',
                '.git', '.svn', '.hg', '.DS_Store',
                'node_modules', '.env', '*.log'
            ]
        }

        # Initialize default configuration if needed
        if not self.config_file.exists():
            self._save_sync_config()

    def add_sync_path(self, path: str, tags: Optional[List[str]] = None,
                     include_patterns: Optional[List[str]] = None,
                     exclude_patterns: Optional[List[str]] = None):
        """Add a path to be synchronized.

        Args:
            path: Directory or file path to sync
            tags: Tags to apply to synced documents
            include_patterns: File patterns to include
            exclude_patterns: File patterns to exclude
        """
        tags = tags or []
        include_patterns = include_patterns or self.default_patterns['include']
        exclude_patterns = exclude_patterns or self.default_patterns['exclude']

        sync_entry = {
            'path': str(Path(path).resolve()),
            'tags': tags,
            'include_patterns': include_patterns,
            'exclude_patterns': exclude_patterns,
            'enabled': True,
            'last_sync': None,
            'auto_sync': True
        }

        # Add or update sync path
        if 'sync_paths' not in self.sync_config:
            self.sync_config['sync_paths'] = []

        # Remove existing entry for same path
        self.sync_config['sync_paths'] = [
            entry for entry in self.sync_config['sync_paths']
            if entry['path'] != sync_entry['path']
        ]

        self.sync_config['sync_paths'].append(sync_entry)
        self._save_sync_config()

        print(f"✅ Added sync path: {path}")
        print(f"   Tags: {tags}")
        print(f"   Include patterns: {len(include_patterns)}")
        print(f"   Exclude patterns: {len(exclude_patterns)}")

    def remove_sync_path(self, path: str):
        """Remove a path from synchronization.

        Args:
            path: Path to remove from sync
        """
        resolved_path = str(Path(path).resolve())

        if 'sync_paths' in self.sync_config:
            original_count = len(self.sync_config['sync_paths'])
            self.sync_config['sync_paths'] = [
                entry for entry in self.sync_config['sync_paths']
                if entry['path'] != resolved_path
            ]

            if len(self.sync_config['sync_paths']) < original_count:
                self._save_sync_config()
                print(f"✅ Removed sync path: {path}")

                # Remove documents from registry
                self._remove_documents_by_path(resolved_path)
            else:
                print(f"❌ Sync path not found: {path}")

    def sync_all(self, force: bool = False) -> SyncStats:
        """Synchronize all configured paths.

        Args:
            force: Force sync even if files haven't changed

        Returns:
            Sync statistics
        """
        start_time = time.time()
        stats = SyncStats(
            total_docs=0,
            synced_docs=0,
            failed_docs=0,
            updated_docs=0,
            new_docs=0,
            sync_time=0.0,
            last_sync=datetime.now().isoformat()
        )

        print("🔄 Starting knowledge base synchronization...")

        # Load current memory store
        memory_data = self._load_memory_store()

        # Process each sync path
        for sync_entry in self.sync_config.get('sync_paths', []):
            if not sync_entry.get('enabled', True):
                continue

            path = Path(sync_entry['path'])
            if not path.exists():
                print(f"[WARN] Sync path not found: {path}")
                continue

            print(f"📁 Syncing: {path}")

            # Find files to sync
            files_to_sync = self._find_files_to_sync(path, sync_entry)
            stats.total_docs += len(files_to_sync)

            # Sync each file
            for file_path in files_to_sync:
                try:
                    result = self._sync_file(file_path, sync_entry, memory_data, force)

                    if result['synced']:
                        stats.synced_docs += 1
                        if result['is_new']:
                            stats.new_docs += 1
                        if result['is_updated']:
                            stats.updated_docs += 1
                    else:
                        stats.failed_docs += 1

                except Exception as e:
                    print(f"❌ Failed to sync {file_path}: {e}")
                    stats.failed_docs += 1

            # Update last sync time
            sync_entry['last_sync'] = datetime.now().isoformat()

        # Save updated memory store and registry
        self._save_memory_store(memory_data)
        self._save_document_registry()
        self._save_sync_config()

        # Complete stats
        stats.sync_time = time.time() - start_time
        self._save_sync_stats(stats)

        print(f"✅ Sync completed in {stats.sync_time:.2f}s")
        print(f"   Total: {stats.total_docs}, Synced: {stats.synced_docs}")
        print(f"   New: {stats.new_docs}, Updated: {stats.updated_docs}")
        print(f"   Failed: {stats.failed_docs}")

        return stats

    def start_auto_sync(self, interval_seconds: int = 300):
        """Start automatic synchronization.

        Args:
            interval_seconds: Sync interval in seconds (default: 5 minutes)
        """
        if self.auto_sync_enabled:
            print("[WARN] Auto-sync already enabled")
            return

        self.auto_sync_enabled = True

        # Start background sync thread
        self.sync_thread = threading.Thread(target=self._auto_sync_worker, args=(interval_seconds,))
        self.sync_thread.daemon = True
        self.sync_thread.start()

        print(f"✅ Auto-sync enabled (interval: {interval_seconds}s)")

    def stop_auto_sync(self):
        """Stop automatic synchronization."""
        self.auto_sync_enabled = False

        if self.sync_thread:
            self.sync_thread.join(timeout=10)
            self.sync_thread = None

        print("✅ Auto-sync disabled")

    def search_documents(self, query: str, tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Search synchronized documents.

        Args:
            query: Search query
            tags: Filter by tags

        Returns:
            List of matching documents
        """
        memory_data = self._load_memory_store()
        results = []

        # Search through synced documents
        for memory_key, content in memory_data.get('memory', {}).items():
            # Check if this is a synced document
            doc_info = next(
                (doc for doc in self.document_registry.values()
                 if doc.memory_key == memory_key), None
            )

            if not doc_info:
                continue

            # Filter by tags
            if tags:
                doc_tags = set(doc_info.tags)
                if not set(tags).issubset(doc_tags):
                    continue

            # Search in content
            content_str = str(content).lower()
            query_lower = query.lower()

            if query_lower in content_str:
                # Calculate relevance score
                score = content_str.count(query_lower)

                results.append({
                    'doc_path': doc_info.doc_path,
                    'memory_key': memory_key,
                    'doc_type': doc_info.doc_type,
                    'tags': doc_info.tags,
                    'score': score,
                    'last_modified': doc_info.last_modified,
                    'preview': self._extract_preview(content_str, query_lower)
                })

        # Sort by relevance score
        results.sort(key=lambda x: x['score'], reverse=True)

        return results

    def get_sync_status(self) -> Dict[str, Any]:
        """Get current synchronization status.

        Returns:
            Sync status information
        """
        stats = self._load_sync_stats()

        return {
            'auto_sync_enabled': self.auto_sync_enabled,
            'sync_paths_count': len(self.sync_config.get('sync_paths', [])),
            'synced_documents': len(self.document_registry),
            'last_sync': stats.get('last_sync') if stats else None,
            'last_sync_stats': stats,
            'sync_paths': [
                {
                    'path': entry['path'],
                    'enabled': entry.get('enabled', True),
                    'auto_sync': entry.get('auto_sync', True),
                    'tags': entry.get('tags', []),
                    'last_sync': entry.get('last_sync')
                }
                for entry in self.sync_config.get('sync_paths', [])
            ]
        }

    def _find_files_to_sync(self, base_path: Path, sync_entry: Dict[str, Any]) -> List[Path]:
        """Find files that should be synchronized."""
        files = []
        include_patterns = sync_entry.get('include_patterns', self.default_patterns['include'])
        exclude_patterns = sync_entry.get('exclude_patterns', self.default_patterns['exclude'])

        if base_path.is_file():
            if self._matches_patterns(base_path, include_patterns, exclude_patterns):
                files.append(base_path)
        else:
            # Recursively find files
            for file_path in base_path.rglob('*'):
                if file_path.is_file():
                    if self._matches_patterns(file_path, include_patterns, exclude_patterns):
                        files.append(file_path)

        return files

    def _matches_patterns(self, file_path: Path, include_patterns: List[str],
                         exclude_patterns: List[str]) -> bool:
        """Check if file matches include/exclude patterns."""
        import fnmatch

        file_name = file_path.name
        file_str = str(file_path)

        # Check exclude patterns first
        for pattern in exclude_patterns:
            if fnmatch.fnmatch(file_name, pattern) or pattern in file_str:
                return False

        # Check include patterns
        for pattern in include_patterns:
            if fnmatch.fnmatch(file_name, pattern):
                return True

        return False

    def _sync_file(self, file_path: Path, sync_entry: Dict[str, Any],
                  memory_data: Dict[str, Any], force: bool = False) -> Dict[str, bool]:
        """Sync a single file to memory store."""
        file_str = str(file_path)

        # Calculate file hash
        content_hash = self._calculate_file_hash(file_path)

        # Check if file needs syncing
        existing_doc = self.document_registry.get(file_str)
        if existing_doc and not force:
            if existing_doc.content_hash == content_hash:
                return {'synced': True, 'is_new': False, 'is_updated': False}

        # Read and process file content
        try:
            content = self._read_file_content(file_path)
            processed_content = self._process_content(content, file_path)

            # Generate memory key
            memory_key = self._generate_memory_key(file_path, sync_entry)

            # Store in memory
            if 'memory' not in memory_data:
                memory_data['memory'] = {}
            memory_data['memory'][memory_key] = processed_content

            # Update tags
            if 'tags' not in memory_data:
                memory_data['tags'] = {}

            doc_tags = sync_entry.get('tags', []) + [f"file_type:{file_path.suffix}"]
            memory_data['tags'][memory_key] = doc_tags

            # Update document registry
            doc_info = DocumentInfo(
                doc_path=file_str,
                memory_key=memory_key,
                last_modified=datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                content_hash=content_hash,
                doc_type=self._detect_doc_type(file_path),
                tags=doc_tags,
                metadata={
                    'size_bytes': file_path.stat().st_size,
                    'sync_path': sync_entry['path']
                }
            )

            is_new = file_str not in self.document_registry
            self.document_registry[file_str] = doc_info

            return {'synced': True, 'is_new': is_new, 'is_updated': not is_new}

        except Exception as e:
            print(f"❌ Error syncing {file_path}: {e}")
            return {'synced': False, 'is_new': False, 'is_updated': False}

    def _read_file_content(self, file_path: Path) -> str:
        """Read file content with appropriate encoding."""
        encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252']

        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
            except Exception:
                break

        # Fallback to binary reading for non-text files
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                return f"[Binary file: {file_path.suffix}, {len(content)} bytes]"
        except Exception as e:
            return f"[Error reading file: {e}]"

    def _process_content(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Process file content for storage in memory."""
        processed: Dict[str, Any] = {
            'raw_content': content,
            'file_path': str(file_path),
            'file_type': file_path.suffix,
            'sync_timestamp': datetime.now().isoformat()
        }

        # Process Markdown files
        if file_path.suffix.lower() in ['.md', '.markdown']:
            processed['headings'] = self._extract_headings(content)

        # Process code files
        elif file_path.suffix.lower() in ['.py', '.js', '.ts', '.java', '.cpp', '.c']:
            processed['functions'] = self._extract_functions(content, file_path.suffix)
            processed['classes'] = self._extract_classes(content, file_path.suffix)

        # Process JSON files
        elif file_path.suffix.lower() == '.json':
            try:
                json_data = json.loads(content)
                processed['json_data'] = json_data
                processed['json_keys'] = list(json_data.keys()) if isinstance(json_data, dict) else []
            except Exception as e:
                processed['json_error'] = str(e)

        return processed

    def _extract_headings(self, markdown_content: str) -> List[Dict[str, Any]]:
        """Extract headings from Markdown content."""
        headings = []
        lines = markdown_content.split('\n')

        for i, line in enumerate(lines):
            if line.strip().startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                title = line.strip('#').strip()
                headings.append({
                    'level': level,
                    'title': title,
                    'line_number': i + 1
                })

        return headings

    def _extract_functions(self, content: str, file_ext: str) -> List[Dict[str, Any]]:
        """Extract function definitions from code."""
        functions = []

        if file_ext == '.py':
            # Python function pattern
            pattern = r'^def\s+(\w+)\s*\((.*?)\):'
            for match in re.finditer(pattern, content, re.MULTILINE):
                functions.append({
                    'name': match.group(1),
                    'parameters': match.group(2),
                    'line': content[:match.start()].count('\n') + 1
                })

        elif file_ext in ['.js', '.ts']:
            # JavaScript/TypeScript function patterns
            patterns = [
                r'function\s+(\w+)\s*\((.*?)\)',
                r'(\w+)\s*:\s*function\s*\((.*?)\)',
                r'(\w+)\s*=\s*\((.*?)\)\s*=>'
            ]

            for pattern in patterns:
                for match in re.finditer(pattern, content, re.MULTILINE):
                    functions.append({
                        'name': match.group(1),
                        'parameters': match.group(2) if len(match.groups()) > 1 else '',
                        'line': content[:match.start()].count('\n') + 1
                    })

        return functions

    def _extract_classes(self, content: str, file_ext: str) -> List[Dict[str, Any]]:
        """Extract class definitions from code."""
        classes = []

        if file_ext == '.py':
            pattern = r'^class\s+(\w+)(?:\((.*?)\))?:'
            for match in re.finditer(pattern, content, re.MULTILINE):
                classes.append({
                    'name': match.group(1),
                    'inheritance': match.group(2) if match.group(2) else '',
                    'line': content[:match.start()].count('\n') + 1
                })

        elif file_ext in ['.js', '.ts']:
            pattern = r'class\s+(\w+)(?:\s+extends\s+(\w+))?'
            for match in re.finditer(pattern, content, re.MULTILINE):
                classes.append({
                    'name': match.group(1),
                    'inheritance': match.group(2) if match.group(2) else '',
                    'line': content[:match.start()].count('\n') + 1
                })

        return classes

    def _generate_memory_key(self, file_path: Path, sync_entry: Dict[str, Any]) -> str:
        """Generate a memory key for the file."""
        # Create a readable, hierarchical key
        base_path = Path(sync_entry['path'])

        try:
            relative_path = file_path.relative_to(base_path)
        except ValueError:
            relative_path = file_path

        # Clean up the path for use as a memory key
        key_parts = ['docs'] + list(relative_path.parts)
        key = '/'.join(part.replace(' ', '_').replace('.', '_') for part in key_parts)

        return key

    def _detect_doc_type(self, file_path: Path) -> str:
        """Detect document type based on file extension."""
        ext = file_path.suffix.lower()

        if ext in ['.md', '.markdown']:
            return 'markdown'
        elif ext in ['.txt', '.text']:
            return 'text'
        elif ext in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.h']:
            return 'code'
        elif ext in ['.json', '.yaml', '.yml']:
            return 'data'
        else:
            return 'unknown'

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file content."""
        sha256_hash = hashlib.sha256()

        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except Exception:
            return ""

    def _extract_preview(self, content: str, query: str, context_chars: int = 150) -> str:
        """Extract a preview around the query match."""
        query_pos = content.lower().find(query.lower())
        if query_pos == -1:
            return content[:context_chars] + "..." if len(content) > context_chars else content

        start = max(0, query_pos - context_chars // 2)
        end = min(len(content), query_pos + len(query) + context_chars // 2)

        preview = content[start:end]
        if start > 0:
            preview = "..." + preview
        if end < len(content):
            preview = preview + "..."

        return preview

    def _auto_sync_worker(self, interval_seconds: int):
        """Background worker for automatic synchronization."""
        while self.auto_sync_enabled:
            try:
                print("🔄 Running auto-sync...")
                self.sync_all()

                # Wait for next cycle
                time.sleep(interval_seconds)

            except Exception as e:
                print(f"[WARN] Auto-sync worker error: {e}")
                time.sleep(60)  # Wait 1 minute before retrying

    def _remove_documents_by_path(self, base_path: str):
        """Remove documents from registry that are under the given path."""
        to_remove = []

        for doc_path, doc_info in self.document_registry.items():
            if doc_path.startswith(base_path):
                to_remove.append(doc_path)

        # Remove from registry
        for doc_path in to_remove:
            del self.document_registry[doc_path]

        # Remove from memory store
        if to_remove:
            memory_data = self._load_memory_store()

            for doc_path in to_remove:
                # Find and remove memory entries
                for memory_key in list(memory_data.get('memory', {}).keys()):
                    content = memory_data['memory'][memory_key]
                    if isinstance(content, dict) and content.get('file_path') == doc_path:
                        del memory_data['memory'][memory_key]
                        if memory_key in memory_data.get('tags', {}):
                            del memory_data['tags'][memory_key]

            self._save_memory_store(memory_data)

        if to_remove:
            print(f"   Removed {len(to_remove)} documents from memory")

    def _load_memory_store(self) -> Dict[str, Any]:
        """Load the memory store data."""
        try:
            if self.memory_store_path.exists():
                with open(self.memory_store_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"[WARN] Error loading memory store: {e}")

        return {'memory': {}, 'tags': {}, 'pins': []}

    def _save_memory_store(self, memory_data: Dict[str, Any]):
        """Save the memory store data."""
        try:
            with open(self.memory_store_path, 'w', encoding='utf-8') as f:
                json.dump(memory_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[WARN] Error saving memory store: {e}")

    def _load_sync_config(self) -> Dict[str, Any]:
        """Load sync configuration."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"[WARN] Error loading sync config: {e}")

        return {
            'sync_paths': [],
            'auto_sync_interval': 300,
            'max_file_size_mb': 10
        }

    def _save_sync_config(self):
        """Save sync configuration."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.sync_config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[WARN] Error saving sync config: {e}")

    def _load_document_registry(self) -> Dict[str, DocumentInfo]:
        """Load document registry."""
        try:
            if self.registry_file.exists():
                with open(self.registry_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return {
                        path: DocumentInfo(**info)
                        for path, info in data.items()
                    }
        except Exception as e:
            print(f"[WARN] Error loading document registry: {e}")

        return {}

    def _save_document_registry(self):
        """Save document registry."""
        try:
            data = {
                path: asdict(info)
                for path, info in self.document_registry.items()
            }
            with open(self.registry_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[WARN] Error saving document registry: {e}")

    def _load_sync_stats(self) -> Optional[Dict[str, Any]]:
        """Load sync statistics."""
        try:
            if self.stats_file.exists():
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"[WARN] Error loading sync stats: {e}")

        return None

    def _save_sync_stats(self, stats: SyncStats):
        """Save sync statistics."""
        try:
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(stats), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[WARN] Error saving sync stats: {e}")


def main():
    """Main function for CLI usage."""
    import sys

    kb_sync = KnowledgeBaseSync()

    if len(sys.argv) < 2:
        print("Usage: python knowledge_base_sync.py <command> [args]")
        print("Commands:")
        print("  add-path <path> [tags...]      - Add sync path")
        print("  remove-path <path>             - Remove sync path")
        print("  sync [--force]                 - Sync all paths")
        print("  start-auto [interval]          - Start auto-sync")
        print("  stop-auto                      - Stop auto-sync")
        print("  search <query> [tags...]       - Search documents")
        print("  status                         - Show sync status")
        return

    command = sys.argv[1]

    try:
        if command == "add-path":
            if len(sys.argv) < 3:
                print("❌ Path required")
                return

            path = sys.argv[2]
            tags = sys.argv[3:] if len(sys.argv) > 3 else None
            kb_sync.add_sync_path(path, tags)

        elif command == "remove-path":
            if len(sys.argv) < 3:
                print("❌ Path required")
                return

            path = sys.argv[2]
            kb_sync.remove_sync_path(path)

        elif command == "sync":
            force = "--force" in sys.argv
            stats = kb_sync.sync_all(force)
            print(f"Sync completed: {stats.synced_docs}/{stats.total_docs} files")

        elif command == "start-auto":
            interval = int(sys.argv[2]) if len(sys.argv) > 2 else 300
            kb_sync.start_auto_sync(interval)
            print("Auto-sync started. Press Ctrl+C to stop.")

            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                kb_sync.stop_auto_sync()
                print("\nAuto-sync stopped")

        elif command == "stop-auto":
            kb_sync.stop_auto_sync()

        elif command == "search":
            if len(sys.argv) < 3:
                print("❌ Search query required")
                return

            query = sys.argv[2]
            tags = sys.argv[3:] if len(sys.argv) > 3 else None

            results = kb_sync.search_documents(query, tags)
            print(f"🔍 Found {len(results)} matching documents:")

            for result in results[:10]:  # Show top 10
                print(f"  📄 {result['doc_path']}")
                print(f"     Type: {result['doc_type']}, Score: {result['score']}")
                print(f"     Preview: {result['preview'][:100]}...")
                print()

        elif command == "status":
            status = kb_sync.get_sync_status()
            print("📊 Knowledge Base Sync Status:")
            print(f"  Auto-sync: {'Enabled' if status['auto_sync_enabled'] else 'Disabled'}")
            print(f"  Sync paths: {status['sync_paths_count']}")
            print(f"  Synced documents: {status['synced_documents']}")
            print(f"  Last sync: {status['last_sync'] or 'Never'}")

            if status['sync_paths']:
                print("\n📁 Sync Paths:")
                for path_info in status['sync_paths']:
                    status_icon = "✅" if path_info['enabled'] else "❌"
                    auto_icon = "🔄" if path_info['auto_sync'] else "⏸️"
                    print(f"  {status_icon}{auto_icon} {path_info['path']}")
                    if path_info['tags']:
                        print(f"     Tags: {', '.join(path_info['tags'])}")

        else:
            print(f"Unknown command: {command}")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
