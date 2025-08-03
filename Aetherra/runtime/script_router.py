# aetherra/runtime/script_router.py

import re

from Aetherra.runtime.script_registry_loader import script_registry_loader
from Aetherra.runtime.script_runner import ScriptRunner


class ScriptRouter:
    def __init__(self, context):
        self.runner = ScriptRunner()
        self.context = (
            context  # Dictionary: {"memory": ..., "plugins": ..., "agents": ...}
        )
        self.registry = script_registry_loader.get_registry()

    def suggest_script(self, goal: str) -> str:
        """Suggest scripts based on goal or intent"""
        goal_lower = goal.lower()
        suggestions = []

        # Get all scripts from registry
        scripts = self.registry.get("scripts", {}) if self.registry else {}

        for script_name, script_data in scripts.items():
            # Check if goal matches tags, description, or commands
            tags = script_data.get("tags", [])
            description = script_data.get("description", "").lower()
            commands = script_data.get("commands", [])

            # Score based on relevance
            score = 0

            # Check tags
            for tag in tags:
                if tag.lower() in goal_lower:
                    score += 3

            # Check description
            if any(word in description for word in goal_lower.split()):
                score += 2

            # Check commands
            for command in commands:
                if command.lower() in goal_lower:
                    score += 4

            # Check use cases
            use_cases = script_data.get("use_cases", [])
            for use_case in use_cases:
                if any(word in use_case.lower() for word in goal_lower.split()):
                    score += 1

            if score > 0:
                suggestions.append(
                    {
                        "name": script_name,
                        "score": score,
                        "description": script_data.get("description", ""),
                        "category": script_data.get("category", ""),
                        "execution_time": script_data.get("execution_time", ""),
                        "complexity": script_data.get("complexity", ""),
                    }
                )

        # Sort by score (highest first)
        suggestions.sort(key=lambda x: x["score"], reverse=True)

        if not suggestions:
            return f"❌ No matching scripts found for goal: '{goal}'"

        # Format response
        response = f"🤖 **Script Suggestions for '{goal}':**\n\n"

        for i, suggestion in enumerate(suggestions[:3]):  # Top 3 suggestions
            response += (
                f"{i + 1}. **{suggestion['name']}** ({suggestion['category']})\n"
            )
            response += f"   {suggestion['description']}\n"
            response += f"   ⏱️ {suggestion['execution_time']} | [TOOL] {suggestion['complexity']}\n\n"

        if len(suggestions) > 3:
            response += f"... and {len(suggestions) - 3} more scripts available.\n"

        return response

    def get_script_categories(self) -> str:
        """Get all available script categories"""
        categories = script_registry_loader.get_categories()

        if not categories:
            return "❌ No script categories found."

        response = "📚 **Available Script Categories:**\n\n"

        for category, info in categories.items():
            scripts = script_registry_loader.get_scripts_by_category(category)
            response += (
                f"{info['icon']} **{category.title()}** ({info['priority']} priority)\n"
            )
            response += f"   {info['description']}\n"
            response += f"   📝 {len(scripts)} scripts available\n\n"

        return response

    def get_script_by_category(self, category: str) -> str:
        """Get scripts in a specific category"""
        scripts = script_registry_loader.get_scripts_by_category(category)

        if not scripts:
            return f"❌ No scripts found in category: '{category}'"

        response = f"📋 **Scripts in '{category}' category:**\n\n"

        for script_name, script_data in scripts.items():
            response += f"• **{script_name}**: {script_data['description']}\n"
            response += f"  ⏱️ {script_data.get('execution_time', 'N/A')} | [TOOL] {script_data.get('complexity', 'N/A')}\n\n"

        return response

    def handle_input(self, user_input: str) -> str:
        # Normalize input
        command = user_input.strip().lower()

        # Match suggest command
        suggest_match = re.match(r"suggest (?:scripts? for )?(.+)", command)
        if suggest_match:
            goal = suggest_match.group(1).strip()
            return self.suggest_script(goal)

        # Match categories command
        if "categories" in command or "show categories" in command:
            return self.get_script_categories()

        # Match category-specific listing
        category_match = re.match(r"(?:list|show) (.+) scripts?", command)
        if category_match:
            category = category_match.group(1).strip()
            return self.get_script_by_category(category)

        # Match run command
        run_match = re.match(r"run (.+?)(\.aether)?$", command)
        if run_match:
            name = run_match.group(1).strip()
            try:
                return self.runner.run_script(name, self.context)
            except Exception as e:
                return f"❌ Failed to run '{name}': {str(e)}"

        # Match list command
        if "list scripts" in command or "available scripts" in command:
            scripts = self.runner.list_scripts()
            if not scripts:
                return "No scripts found in standard library."
            response = "📚 **Available Scripts:**\n\n"
            for script in scripts:
                response += f"• **{script['name']}** ({script['category']}): {script['description']}\n"
            return response

        # Match description request
        desc_match = re.match(r"describe (.+?)(\.aether)?$", command)
        if desc_match:
            name = desc_match.group(1).strip()
            for script in self.runner.list_scripts():
                if script["name"] == name:
                    return f"📝 **{name}**: {script['description']}\nTags: {', '.join(script['tags'])}"
            return f"Script '{name}' not found."

        return "🤖 I can help you with scripts! Try:\n• 'list scripts' - Show all available scripts\n• 'suggest [goal]' - Get script suggestions for a goal\n• 'categories' - Show script categories\n• 'run [name]' - Execute a script\n• 'describe [name]' - Get script details"


# Example usage (for testing purposes)
if __name__ == "__main__":
    dummy_context = {"memory": None, "plugins": None, "agents": None}
    router = ScriptRouter(context=dummy_context)

    print(router.handle_input("list scripts"))
    print(router.handle_input("describe summarize_day"))
    print(router.handle_input("run bootstrap"))
