# plugin_editor_refactor.py
# ✅ Integration code to enable function/class replacement in Lyrixa's Plugin Editor
# 🧠 Enhanced with AST-aware editing capabilities

import re

# Try to import the advanced editor for enhanced capabilities
try:
    from .advanced_code_editor import ASTAwareCodeEditor
    ADVANCED_EDITOR_AVAILABLE = True
    _advanced_editor = ASTAwareCodeEditor()
    print("✅ Advanced AST-aware code editor loaded")
except ImportError:
    ADVANCED_EDITOR_AVAILABLE = False
    _advanced_editor = None
    print("⚠️ Advanced editor not available - using basic refactor mode")

def replace_block(existing_code: str, new_block: str) -> str:
    """
    Replaces an existing function or class in the plugin code with a new version.

    Args:
        existing_code: The current plugin code
        new_block: The new function/class code to replace with

    Returns:
        Updated code with the block replaced
    """
    # Extract function or class signature from new_block
    signature_match = re.search(r'(def|class)\s+(\w+)\s*\(?.*?:', new_block)
    if not signature_match:
        return existing_code  # Can't process if no valid signature found

    block_type = signature_match.group(1)
    block_name = signature_match.group(2)

    # Build regex to match the entire original function/class block
    # Matches indentation-based Python blocks safely
    pattern = rf'({block_type}\s+{block_name}\s*\(?.*?:\n(?:[ \t]+.+\n)+)'  # match function/class with its block
    match = re.search(pattern, existing_code)

    if match:
        start, end = match.span()
        return existing_code[:start] + new_block + existing_code[end:]
    else:
        # Fallback: Append to end if not found
        return existing_code.strip() + '\n\n' + new_block


def smart_code_merge(existing_code: str, new_code: str, merge_strategy: str = "intelligent") -> str:
    """
    Advanced code merging with multiple strategies for plugin editing.
    🧠 Enhanced with AST-aware capabilities when available.

    Args:
        existing_code: Current plugin code
        new_code: New code to integrate
        merge_strategy: "replace", "append", "intelligent", "block_replace", or "ast_aware"

    Returns:
        Merged code based on strategy
    """
    # Use advanced editor if available and strategy allows
    if ADVANCED_EDITOR_AVAILABLE and _advanced_editor and merge_strategy in ["intelligent", "ast_aware"]:
        try:
            merged_code, success, message = _advanced_editor.intelligent_code_merge(
                existing_code, new_code, f"Smart merge with strategy: {merge_strategy}"
            )
            if success:
                print(f"✅ AST-aware merge successful: {message}")
                return merged_code
            else:
                print(f"⚠️ AST-aware merge failed: {message}, falling back to basic merge")
        except Exception as e:
            print(f"⚠️ Advanced editor error: {e}, falling back to basic merge")

    # Fallback to basic merging
    if merge_strategy == "replace":
        return new_code
    elif merge_strategy == "append":
        if not existing_code.endswith('\n'):
            existing_code += '\n'
        return existing_code + '\n# ✏️ Additional functionality:\n' + new_code
    elif merge_strategy == "block_replace":
        return replace_block(existing_code, new_code)
    elif merge_strategy == "intelligent":
        # Try to determine the best strategy automatically
        if _contains_function_or_class(new_code) and _has_matching_signature(existing_code, new_code):
            return replace_block(existing_code, new_code)
        elif len(new_code) > len(existing_code) and existing_code.strip() in new_code:
            return new_code  # New code contains existing - safe to replace
        else:
            return smart_code_merge(existing_code, new_code, "append")
    else:
        return existing_code


def _contains_function_or_class(code: str) -> bool:
    """Check if code contains function or class definitions"""
    return bool(re.search(r'(def|class)\s+\w+\s*\(?.*?:', code))


def _has_matching_signature(existing_code: str, new_code: str) -> bool:
    """Check if new code has a matching function/class signature in existing code"""
    new_signature = re.search(r'(def|class)\s+(\w+)\s*\(?.*?:', new_code)
    if not new_signature:
        return False

    block_type = new_signature.group(1)
    block_name = new_signature.group(2)

    existing_pattern = rf'{block_type}\s+{block_name}\s*\(?.*?:'
    return bool(re.search(existing_pattern, existing_code))


def parse_plugin_metadata(code: str):
    """
    🔍 Parse plugin metadata using advanced editor
    """
    if ADVANCED_EDITOR_AVAILABLE and _advanced_editor:
        return _advanced_editor.parse_plugin_metadata(code)
    return None

def analyze_code_structure(code: str):
    """
    🧠 Analyze code structure using AST
    """
    if ADVANCED_EDITOR_AVAILABLE and _advanced_editor:
        return _advanced_editor.analyze_code_structure(code)
    return {'valid_syntax': True, 'message': 'Basic analysis - advanced editor not available'}

def get_learning_insights():
    """
    📊 Get editing learning insights
    """
    if ADVANCED_EDITOR_AVAILABLE and _advanced_editor:
        return _advanced_editor.get_learning_insights()
    return {'message': 'Learning insights not available - advanced editor not loaded'}

def generate_test_case_for_function(function_info: dict) -> str:
    """
    🧪 Generate test case for a function
    """
    if ADVANCED_EDITOR_AVAILABLE and _advanced_editor:
        return _advanced_editor.generate_test_case(function_info)

    # Fallback basic test generation
    func_name = function_info.get('name', 'unknown_function')
    return f"""
def test_{func_name}():
    '''Basic test for {func_name}'''
    # TODO: Implement proper test
    pass
"""

def create_metadata_template(plugin_name: str, functions=None, classes=None,
                           version: str = "1.0", description: str = "") -> str:
    """
    📝 Create metadata template for plugin
    """
    functions = functions or []
    classes = classes or []

    template = f'''# @plugin: {plugin_name}
# @functions: {', '.join(functions)}
# @classes: {', '.join(classes)}
# @version: {version}
# @description: {description}

"""
{description}
Version: {version}
"""

'''
    return template

# ✅ Example usage (to integrate inside Lyrixa editor controller)
if __name__ == "__main__":
    original_code = '''
class APIMonitor:
    def __init__(self, api_url):
        self.api_url = api_url

    async def check_status(self):
        print("Old check_status implementation")
'''

    improved_code = '''    async def check_status(self):
        print("New improved check_status")
        return {"status": "enhanced"}'''

    updated_code = replace_block(original_code, improved_code)
    print("=== Original Code ===")
    print(original_code)
    print("\n=== Improved Code Block ===")
    print(improved_code)
    print("\n=== Updated Result ===")
    print(updated_code)
