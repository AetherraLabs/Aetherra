# core/debug_system.py
"""
Automatic Debug and Self-Correction System for Neuroplex
Detects errors, suggests fixes, and applies corrections automatically
"""

import os
import sys
import traceback
import ast
import difflib
import shutil
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import subprocess

from .aetherra_memory import AetherraMemory
from .ai_runtime import ask_ai

class NeuroDebugSystem:
    """Automatic error detection, analysis, and self-correction system"""
    
    def __init__(self, memory: AetherraMemory):
        self.memory = memory
        self.error_history = []
        self.fix_confidence_threshold = 80
        self.auto_apply_enabled = False
        self.backup_dir = "backups/debug"
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def detect_and_store_error(self, error: Exception, context: str = "", file_path: str = ""):
        """Step 1: Error Detection - Catch and store errors in memory"""
        error_info = {
            "type": type(error).__name__,
            "message": str(error),
            "context": context,
            "file_path": file_path,
            "traceback": traceback.format_exc(),
            "timestamp": str(datetime.now()),
            "line_number": self._extract_line_number(error)
        }
        
        # Store in memory with debug tag
        error_description = f"{error_info['type']}: {error_info['message']}"
        if error_info['line_number']:
            error_description += f" at line {error_info['line_number']}"
        if file_path:
            error_description += f" in {os.path.basename(file_path)}"
        
        self.memory.remember(error_description, tags=["debug", "error"], category="debugging")
        self.error_history.append(error_info)
        
        print(f"🐛 [Debug] Error detected and stored: {error_description}")
        return error_info
    
    def _extract_line_number(self, error: Exception) -> Optional[int]:
        """Extract line number from error if available"""
        # For SyntaxError and similar exceptions that have lineno
        if hasattr(error, 'lineno'):
            lineno = getattr(error, 'lineno', None)
            if lineno is not None:
                return lineno
        
        # Try to extract from traceback
        if error.__traceback__:
            tb = traceback.extract_tb(error.__traceback__)
            if tb:
                return tb[-1].lineno
        return None
    
    def suggest_fix(self, error_info: Dict) -> Dict:
        """Step 2: AI-Driven Fix Suggestion"""
        print(f"🔧 [Debug] Analyzing error and suggesting fix...")
        
        # Get relevant context
        file_content = ""
        if error_info['file_path'] and os.path.exists(error_info['file_path']):
            with open(error_info['file_path'], 'r', encoding='utf-8') as f:
                file_content = f.read()
        
        # Get related errors from memory
        related_errors = self.memory.recall(tags=["debug", "error"], limit=5)
        
        # Create AI prompt for fix suggestion
        prompt = f"""
NEUROPLEX DEBUG SYSTEM - FIX SUGGESTION

Error Details:
- Type: {error_info['type']}
- Message: {error_info['message']}
- File: {error_info['file_path']}
- Line: {error_info['line_number']}
- Context: {error_info['context']}

File Content:
```python
{file_content[:2000]}{'...' if len(file_content) > 2000 else ''}
```

Traceback:
{error_info['traceback']}

Related Errors from Memory:
{chr(10).join(related_errors[-3:]) if related_errors else 'None'}

Please provide:
1. Root cause analysis
2. Specific fix recommendation
3. Complete corrected code (if file fix needed)
4. Confidence level (0-100%)
5. Risk assessment
6. Prevention strategy

Format your response as:
ANALYSIS: [root cause]
FIX: [specific fix]
CONFIDENCE: [0-100]
RISK: [low/medium/high]
PREVENTION: [strategy]
CODE:
```python
[corrected code if needed]
```
"""
        
        ai_response = ask_ai(prompt, temperature=0.1)
        
        # Parse AI response
        fix_suggestion = self._parse_fix_response(ai_response)
        fix_suggestion['original_error'] = error_info
        fix_suggestion['ai_response'] = ai_response
        
        # Store fix suggestion in memory
        fix_summary = f"Fix suggested for {error_info['type']}: {fix_suggestion.get('fix', 'See details')}"
        self.memory.remember(fix_summary, tags=["debug", "fix", "suggestion"], category="debugging")
        
        print(f"🤖 [Debug] Fix suggested with {fix_suggestion.get('confidence', 0)}% confidence")
        return fix_suggestion
    
    def _parse_fix_response(self, ai_response: str) -> Dict:
        """Parse AI response into structured fix suggestion"""
        fix_info = {
            "analysis": "",
            "fix": "",
            "confidence": 0,
            "risk": "unknown",
            "prevention": "",
            "code": ""
        }
        
        lines = ai_response.split('\n')
        current_section = None
        code_section = False
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('ANALYSIS:'):
                current_section = 'analysis'
                fix_info['analysis'] = line.replace('ANALYSIS:', '').strip()
            elif line.startswith('FIX:'):
                current_section = 'fix'
                fix_info['fix'] = line.replace('FIX:', '').strip()
            elif line.startswith('CONFIDENCE:'):
                try:
                    confidence_str = line.replace('CONFIDENCE:', '').strip()
                    fix_info['confidence'] = int(''.join(filter(str.isdigit, confidence_str)))
                except:
                    fix_info['confidence'] = 50
            elif line.startswith('RISK:'):
                fix_info['risk'] = line.replace('RISK:', '').strip().lower()
            elif line.startswith('PREVENTION:'):
                current_section = 'prevention'
                fix_info['prevention'] = line.replace('PREVENTION:', '').strip()
            elif line.startswith('CODE:'):
                code_section = True
                current_section = 'code'
            elif line.startswith('```python'):
                code_section = True
            elif line.startswith('```'):
                code_section = False
            elif code_section and current_section == 'code':
                fix_info['code'] += line + '\n'
            elif current_section and not code_section:
                fix_info[current_section] += ' ' + line
        
        return fix_info
    
    def apply_fix(self, fix_suggestion: Dict, force: bool = False) -> bool:
        """Step 3: Self-Repair - Apply the suggested fix"""
        confidence = fix_suggestion.get('confidence', 0)
        risk = fix_suggestion.get('risk', 'high')
        
        # Check if we should apply automatically
        if not force and not self.auto_apply_enabled:
            print(f"⚠️ [Debug] Auto-apply disabled. Use 'apply fix force' to apply manually.")
            return False
        
        if not force and confidence < self.fix_confidence_threshold:
            print(f"⚠️ [Debug] Confidence {confidence}% below threshold {self.fix_confidence_threshold}%")
            return False
        
        if not force and risk == 'high':
            print(f"⚠️ [Debug] High risk fix detected. Use 'apply fix force' to override.")
            return False
        
        error_info = fix_suggestion['original_error']
        file_path = error_info['file_path']
        
        if not file_path or not os.path.exists(file_path):
            print(f"❌ [Debug] Cannot apply fix - file not found: {file_path}")
            return False
        
        if not fix_suggestion.get('code'):
            print(f"❌ [Debug] No code provided in fix suggestion")
            return False
        
        try:
            # Create backup
            backup_path = self._create_backup(file_path)
            print(f"💾 [Debug] Backup created: {backup_path}")
            
            # Apply fix
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fix_suggestion['code'].strip())
            
            # Validate the fix
            if self._validate_fix(file_path):
                # Store success in memory
                self.memory.remember(
                    f"Successfully applied fix to {os.path.basename(file_path)}: {fix_suggestion['fix'][:100]}",
                    tags=["debug", "fix", "success"],
                    category="debugging"
                )
                print(f"✅ [Debug] Fix applied successfully to {file_path}")
                return True
            else:
                # Restore backup if validation fails
                shutil.copy2(backup_path, file_path)
                print(f"❌ [Debug] Fix validation failed - backup restored")
                return False
                
        except Exception as e:
            print(f"❌ [Debug] Error applying fix: {e}")
            return False
    
    def _create_backup(self, file_path: str) -> str:
        """Create a backup of the file before applying fix"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.basename(file_path)
        backup_filename = f"{filename}.backup_{timestamp}"
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        shutil.copy2(file_path, backup_path)
        return backup_path
    
    def _validate_fix(self, file_path: str) -> bool:
        """Validate that the fixed file has no syntax errors"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Try to parse as Python
            if file_path.endswith('.py'):
                ast.parse(content)
            
            return True
        except SyntaxError as e:
            print(f"⚠️ [Debug] Syntax error in fixed file: {e}")
            return False
        except Exception as e:
            print(f"⚠️ [Debug] Validation error: {e}")
            return False
    
    def auto_debug_loop(self, error: Exception, context: str = "", file_path: str = "") -> bool:
        """Complete automatic debug loop"""
        print(f"🔄 [Debug] Starting auto-debug loop...")
        
        # Step 1: Detect and store error
        error_info = self.detect_and_store_error(error, context, file_path)
        
        # Step 2: Suggest fix
        fix_suggestion = self.suggest_fix(error_info)
        
        # Step 3: Apply fix if confidence is high enough
        if fix_suggestion.get('confidence', 0) >= self.fix_confidence_threshold:
            return self.apply_fix(fix_suggestion)
        else:
            print(f"🤔 [Debug] Confidence too low for auto-apply. Manual review needed.")
            return False
    
    def set_auto_apply(self, enabled: bool, confidence_threshold: int = 80):
        """Configure automatic fix application"""
        self.auto_apply_enabled = enabled
        self.fix_confidence_threshold = confidence_threshold
        
        status = "enabled" if enabled else "disabled"
        print(f"🔧 [Debug] Auto-apply {status} (confidence threshold: {confidence_threshold}%)")
        
        # Store setting in memory
        self.memory.remember(
            f"Debug auto-apply {status} with {confidence_threshold}% confidence threshold",
            tags=["debug", "settings"],
            category="configuration"
        )
    
    def get_debug_stats(self) -> Dict:
        """Get debugging statistics"""
        error_memories = self.memory.recall(tags=["debug", "error"])
        fix_memories = self.memory.recall(tags=["debug", "fix", "success"])
        
        return {
            "total_errors": len(error_memories),
            "successful_fixes": len(fix_memories),
            "auto_apply_enabled": self.auto_apply_enabled,
            "confidence_threshold": self.fix_confidence_threshold,
            "recent_errors": error_memories[-5:] if error_memories else []
        }
    
    def show_debug_status(self):
        """Display current debug system status"""
        stats = self.get_debug_stats()
        
        print("🐛 DEBUG SYSTEM STATUS")
        print("=" * 30)
        print(f"Auto-apply: {'✅ Enabled' if stats['auto_apply_enabled'] else '❌ Disabled'}")
        print(f"Confidence threshold: {stats['confidence_threshold']}%")
        print(f"Total errors detected: {stats['total_errors']}")
        print(f"Successful fixes: {stats['successful_fixes']}")
        
        if stats['recent_errors']:
            print("\nRecent errors:")
            for error in stats['recent_errors'][-3:]:
                print(f"  • {error}")


# Decorator for automatic error handling
def auto_debug(debug_system: NeuroDebugSystem, file_path: str = ""):
    """Decorator to automatically handle errors in functions"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                debug_system.auto_debug_loop(e, f"Function: {func.__name__}", file_path)
                raise  # Re-raise after debugging
        return wrapper
    return decorator
