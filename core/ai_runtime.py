# core/ai_runtime.py
import os

import openai


# Try to load from .env file if it exists
def load_env_file():
    """Load environment variables from .env file"""
    env_file = os.path.join(os.path.dirname(__file__), "..", ".env")
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()


# Load .env file if it exists
load_env_file()

# Global flag to prevent duplicate initialization
_openai_client_initialized = False

# Initialize OpenAI client with environment variable
api_key = os.getenv("OPENAI_API_KEY")
if api_key and not _openai_client_initialized:
    client = openai.OpenAI(api_key=api_key)
    print(f"[AI] OpenAI client initialized (key ending in ...{api_key[-4:]})")
    _openai_client_initialized = True
elif api_key and _openai_client_initialized:
    # Client already initialized, just create the object without message
    client = openai.OpenAI(api_key=api_key)
else:
    client = None
    if not _openai_client_initialized:
        print(
            "[Warning] OPENAI_API_KEY environment variable not set. AI features will be disabled."
        )
        print("💡 To enable AI features:")
        print("   1. Get an API key from https://platform.openai.com/api-keys")
        print("   2. Set environment variable: set OPENAI_API_KEY=your-key")
        print("   3. Or add it to the .env file in the project root")
        _openai_client_initialized = True


def ask_ai(prompt, temperature=0.2, debug_mode=False, model=None):
    """Enhanced AI query function with detailed logging"""
    if client is None:
        return "[AI Disabled] OPENAI_API_KEY not configured"

    try:
        # Use specified model or try defaults
        models_to_try = [model] if model else ["gpt-4o-mini", "gpt-3.5-turbo", "gpt-4"]

        for current_model in models_to_try:
            try:
                if debug_mode:
                    print(f"🔹 Prompt sent to {current_model}:")
                    print(f"   {prompt[:200]}{'...' if len(prompt) > 200 else ''}")

                response = client.chat.completions.create(
                    model=current_model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                )
                content = response.choices[0].message.content
                result = content.strip() if content is not None else ""

                if debug_mode:
                    print(f"🔸 LLM response from {current_model}:")
                    print(f"   {result[:200]}{'...' if len(result) > 200 else ''}")

                return result
            except Exception as model_error:
                if debug_mode:
                    print(f"❌ Model {current_model} failed: {model_error}")
                if (
                    "model" in str(model_error).lower()
                    and "not" in str(model_error).lower()
                ):
                    continue  # Try next model
                else:
                    raise model_error  # Different error, don't retry

        return "[AI Error] No available models found"
    except Exception as e:
        if debug_mode:
            print(f"❌ AI call failed: {e}")
        return f"[AI Error] {str(e)}"


def analyze_memory_patterns(memories, tag_frequency, category_frequency):
    """AI analysis of memory patterns and behavior suggestions"""
    recent_memories = [m["text"] for m in memories[-10:]]  # Last 10 memories
    content_context = "\n".join(recent_memories)

    prompt = f"""Analyze these recent memories for patterns \and
        suggest 3 specific behaviors or workflows the user should adopt:

Memories:
{content_context}

Tag patterns: {tag_frequency}
Category patterns: {category_frequency}

Provide actionable Aetherra suggestions based on detected patterns."""

    return ask_ai(prompt)


def analyze_user_behavior(
    command_types, recent_commands, functions, memories, command_history_length
):
    """AI analysis of user behavior patterns and optimization suggestions"""
    behavior_context = f"""
Command usage patterns: {command_types}
Recent commands: {recent_commands}
Available functions: {list(functions.keys())}
Total memories: {len(memories)}
Command history length: {command_history_length}
"""

    prompt = f"""Analyze user behavior patterns based on their Aetherra usage:

{behavior_context}

Identify:
1. Usage patterns and habits
2. Most/least used features
3. Areas for optimization
4. Suggested workflow improvements
5. Potential automation opportunities

Provide specific Aetherra recommendations."""

    return ask_ai(prompt)


def suggest_system_evolution(memory_summary, function_count, context=""):
    """AI suggestions for system evolution and improvements"""
    evolution_context = f"""
System State:
- Total memories: {memory_summary["total_memories"]}
- Available tags: {memory_summary["tags"]}
- Categories: {memory_summary["categories"]}
- Defined functions: {function_count}
- User context: {context}

Recent memory sample:
{chr(10).join(memory_summary.get("recent_memories", []))}
"""

    prompt = f"""Based on this Lyrixa system state, suggest evolutionary improvements:

{evolution_context}

Suggest:
1. New Aetherra commands that would be useful
2. System capabilities that should be added
3. Workflow optimizations
4. Memory organization improvements
5. Function templates the user should create

Provide concrete, actionable suggestions."""

    return ask_ai(prompt)


def provide_adaptive_suggestions(
    context, recent_memories, available_tags, function_names
):
    """AI-powered adaptive suggestions based on current context"""
    adaptive_context = f"""
Current Context: {context}
Recent memories: {recent_memories}
Available tags: {available_tags}
Available functions: {function_names}
"""

    prompt = f"""Provide 3-5 adaptive suggestions for the user's next actions in Aetherra:

{adaptive_context}

Consider:
- What they've been working on recently
- Available tools and functions
- Potential knowledge gaps
- Workflow optimizations

Suggest specific Aetherra commands they should run next."""

    return ask_ai(prompt)


def reflect_on_memories(memories, filter_description):
    """AI reflection on filtered memories"""
    context = "\n".join(memories)
    prompt = f"Reflect on and analyze these memories filtered by {filter_description}:\n{context}"
    return ask_ai(prompt)


def auto_tag_content(summary):
    """Generate relevant tags for content automatically"""
    prompt = f"Generate 2-3 relevant tags for this content (comma-separated): {summary}"
    response = ask_ai(prompt)
    return [tag.strip() for tag in response.split(",")]


def suggest_next_actions(summary):
    """Suggest next Aetherra actions based on learned content"""
    prompt = (
        f"Based on this summary, suggest useful Aetherra to execute next:\n{summary}"
    )
    return ask_ai(prompt)


# ==================== SELF-EDITING AI FUNCTIONS =============
def analyze_code_structure(content, filename):
    """Analyze code structure and provide architectural insights"""
    prompt = f"""Analyze the structure and architecture of this code file:

Filename: {filename}
Content:
{content}

Provide insights on:
1. Code organization and structure
2. Design patterns used
3. Potential architectural issues
4. Dependencies and coupling
5. Code quality indicators

Be concise but thorough."""

    return ask_ai(prompt)


def generate_code_summary(content, filename):
    """Generate a concise summary of what the code does"""
    prompt = f"""Provide a concise summary of this code file:

Filename: {filename}
Content:
{content}

Summarize:
1. Main purpose and functionality
2. Key classes/functions
3. Important features
4. Role in the larger system

Keep it brief but informative."""

    return ask_ai(prompt)


def deep_code_analysis(content, filename, memory_context):
    """Perform deep analysis of code for bugs, improvements, and patterns"""
    prompt = f"""Perform a deep analysis of this code for potential issues and improvements:

Filename: {filename}
Content:
{content}

Previous analysis context:
{memory_context}

Analyze for:
1. Potential bugs or errors
2. Performance issues
3. Security vulnerabilities
4. Code smells and anti-patterns
5. Maintainability concerns
6. Testing gaps

Provide specific, actionable feedback."""

    return ask_ai(prompt)


def suggest_code_improvements(content, filename, memory_context):
    """Suggest specific code improvements based on analysis"""
    prompt = f"""Suggest specific improvements for this code:

Filename: {filename}
Content:
{content}

Context from previous analyses:
{memory_context}

Suggest:
1. Refactoring opportunities
2. Performance optimizations
3. Code organization improvements
4. Best practice implementations
5. Error handling enhancements

Prioritize suggestions by impact and feasibility."""

    return ask_ai(prompt)


def suggest_refactoring(content, filename, target, memory_context):
    """Generate refactored code based on specific targets"""
    prompt = f"""Refactor this code focusing on: {target}

Filename: {filename}
Original Content:
{content}

Context from memory:
{memory_context}

Provide the complete refactored code that:
1. Addresses the target improvement: {target}
2. Maintains all existing functionality
3. Follows best practices
4. Is well-documented

Return only the refactored code, ready to replace the original."""

    return ask_ai(prompt, temperature=0.1)  # Lower temperature for code generation


def justify_refactoring(content, target, memory_context):
    """Provide justification for why refactoring is beneficial"""
    prompt = f"""Justify why this refactoring is beneficial:

Target improvement: {target}
Original code preview: {content[:500]}...

Memory context:
{memory_context}

Explain:
1. Why this refactoring is needed
2. What benefits it will provide
3. What risks are mitigated
4. How it aligns with best practices
5. Expected impact on the system

Be persuasive but factual."""

    return ask_ai(prompt)


def memory_driven_code_suggestion(memories, patterns, code_context=""):
    """Use memory patterns to suggest code improvements and self-editing opportunities"""
    recent_patterns = [m["text"] for m in memories if "pattern" in m.get("tags", [])]
    error_patterns = [m["text"] for m in memories if "error" in m.get("tags", [])]

    prompt = f"""Based on memory patterns, suggest self-editing opportunities:

Recent patterns detected: {recent_patterns}
Error patterns found: {error_patterns}
Pattern analysis: {patterns}
Current code context: {code_context}

Suggest:
1. Code files that need attention based on patterns
2. Specific improvements based on recurring issues
3. Self-editing commands to run
4. Why these changes would be beneficial

Provide actionable Aetherra commands."""

    return ask_ai(prompt)


def justify_self_editing_decision(filename, analysis, memory_context):
    """Provide memory-driven justification for self-editing decisions"""
    prompt = f"""Based on memory and analysis, justify self-editing this file:

File: {filename}
Analysis: {analysis}
Memory context: {memory_context}

Explain:
1. What patterns in memory support this change
2. How this addresses recurring issues
3. Expected benefits based on past experiences
4. Risk assessment based on memory patterns
5. Why this is the right time for this change

Be specific and reference memory patterns."""

    return ask_ai(prompt)
