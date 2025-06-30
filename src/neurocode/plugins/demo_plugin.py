# Sample Enhanced Plugin
from core.plugin_manager import register_plugin

@register_plugin(
    name="demo_analyzer",
    description="Analyze text and provide insights with AI-powered capabilities",
    capabilities=["text_analysis", "sentiment_detection", "keyword_extraction", "ai_insights"],
    version="2.0.0",
    author="NeuroCode AI Team",
    category="analysis",
    dependencies=["re", "collections"],
    # Enhanced intent-based discovery
    intent_purpose="text analysis and sentiment detection",
    intent_triggers=["analyze", "sentiment", "text", "insights", "analyze text", "check sentiment"],
    intent_scenarios=[
        "analyzing user feedback or reviews",
        "understanding document sentiment",
        "extracting keywords from content",
        "getting text statistics and insights"
    ],
    ai_description="Provides comprehensive text analysis including word count, sentiment analysis, and keyword extraction. Perfect for understanding content tone and extracting meaningful insights from text data.",
    example_usage="plugin: demo_analyzer 'This is amazing text to analyze!'",
    confidence_boost=1.2
)
def analyze_text(text):
    """Analyze text and return comprehensive insights"""
    import re
    from collections import Counter
    
    # Basic analysis
    word_count = len(text.split())
    char_count = len(text)
    sentence_count = len(re.findall(r'[.!?]+', text))
    
    # Word frequency
    words = re.findall(r'\b\w+\b', text.lower())
    common_words = Counter(words).most_common(5)
    
    # Sentiment simulation (simplified)
    positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic']
    negative_words = ['bad', 'terrible', 'awful', 'horrible', 'disappointing']
    
    positive_count = sum(1 for word in words if word in positive_words)
    negative_count = sum(1 for word in words if word in negative_words)
    
    sentiment = "positive" if positive_count > negative_count else "negative" if negative_count > positive_count else "neutral"
    
    return {
        "word_count": word_count,
        "character_count": char_count,
        "sentence_count": sentence_count,
        "most_common_words": common_words,
        "sentiment": sentiment,
        "sentiment_scores": {"positive": positive_count, "negative": negative_count}
    }

@register_plugin(
    name="code_formatter",
    description="Format and beautify code with intelligent indentation and styling",
    capabilities=["code_formatting", "syntax_highlighting", "style_validation"],
    version="1.5.0",
    author="NeuroCode DevTools",
    category="development",
    dependencies=["re"],
    # Enhanced intent-based discovery
    intent_purpose="code formatting and beautification",
    intent_triggers=["format", "beautify", "indent", "style", "format code", "clean code"],
    intent_scenarios=[
        "formatting messy or unindented code",
        "preparing code for presentation or review",
        "standardizing code style across projects",
        "improving code readability and organization"
    ],
    ai_description="Automatically formats and beautifies code with proper indentation, spacing, and style conventions. Supports multiple programming languages and intelligent bracket matching.",
    example_usage="plugin: code_formatter 'def func():\\nprint(\"hello\")' python",
    confidence_boost=1.1
)
def format_code(code, language="python"):
    """Format code with proper indentation and styling"""
    import re
    
    # Simplified code formatting
    lines = code.split('\n')
    formatted_lines = []
    indent_level = 0
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            formatted_lines.append('')
            continue
            
        # Decrease indent for certain patterns
        if re.match(r'^(end|else|elif|except|finally|\})', stripped):
            indent_level = max(0, indent_level - 1)
        
        # Add indented line
        formatted_lines.append('    ' * indent_level + stripped)
        
        # Increase indent for certain patterns
        if re.search(r'(:|\{|def |class |if |for |while |try:)\s*$', stripped):
            indent_level += 1
    
    return '\n'.join(formatted_lines)
