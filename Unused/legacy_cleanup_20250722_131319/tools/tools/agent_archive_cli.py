#!/usr/bin/env python3
"""
🎯 aetherra Agent Archive CLI
Command-line interface for agent archiving, importing, and replay functionality.

This module provides easy-to-use CLI commands for the Agent Archive & Replay System,
integrating with the existing aetherra CLI infrastructure.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

# Import our archive system modules
try:
    from .agent_archiver import AgentArchiver, export_agent
    from .agent_importer import AgentImporter, import_agent, merge_agents
    from .replay_engine import InteractiveReplayDebugger, ReplayEngine
except ImportError:
    # Fallback for direct execution
    from agent_archiver import AgentArchiver, export_agent
    from agent_importer import AgentImporter, import_agent, merge_agents
    from replay_engine import InteractiveReplayDebugger, ReplayEngine


class AgentArchiveCLI:
    """Command-line interface for agent archive operations"""

    def __init__(self):
        self.archiver = AgentArchiver()
        self.importer = AgentImporter()
        self.replay_engine = ReplayEngine()

    def create_parser(self) -> argparse.ArgumentParser:
        """Create the CLI argument parser"""
        parser = argparse.ArgumentParser(
            prog="aetherra agent",
            description="🧠 aetherra Agent Archive & Replay System",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Export current agent state
  aetherra agent export MyAgent --version 1.0 --description "Production optimizer"

  # Import agent archive
  aetherra agent import MyAgent_v1.0.nse --merge-mode replace

  # Merge two agents
  aetherra agent merge agent1.nse agent2.nse --output merged_agent.nse

  # List available archives
  aetherra agent list

  # Preview archive contents
  aetherra agent preview MyAgent_v1.0.nse

  # Start replay session
  aetherra agent replay MyAgent_v1.0.nse --interactive

  # Analyze decision patterns
  aetherra agent analyze MyAgent_v1.0.nse
            """,
        )

        subparsers = parser.add_subparsers(dest="command", help="Available commands")

        # Export command
        export_parser = subparsers.add_parser("export", help="Export agent to archive")
        export_parser.add_argument("name", help="Agent name")
        export_parser.add_argument("--version", default="1.0", help="Agent version")
        export_parser.add_argument(
            "--description", required=True, help="Agent description"
        )
        export_parser.add_argument(
            "--tags", nargs="*", default=[], help="Tags for categorization"
        )
        export_parser.add_argument(
            "--privacy",
            choices=["private", "team", "public"],
            default="private",
            help="Privacy level",
        )
        export_parser.add_argument("--output-dir", help="Output directory for archive")

        # Import command
        import_parser = subparsers.add_parser(
            "import", help="Import agent from archive"
        )
        import_parser.add_argument("archive", help="Archive file path")
        import_parser.add_argument(
            "--merge-mode",
            choices=["replace", "merge"],
            default="replace",
            help="How to handle existing agent data",
        )
        import_parser.add_argument(
            "--target-agent", help="Target agent name (if different)"
        )
        import_parser.add_argument(
            "--validate",
            action="store_true",
            default=True,
            help="Validate archive before import",
        )

        # Merge command
        merge_parser = subparsers.add_parser("merge", help="Merge two agent archives")
        merge_parser.add_argument("primary", help="Primary agent archive")
        merge_parser.add_argument("secondary", help="Secondary agent archive")
        merge_parser.add_argument("--output", help="Output file for merged archive")
        merge_parser.add_argument(
            "--strategy",
            choices=["intelligent", "additive"],
            default="intelligent",
            help="Merge strategy",
        )

        # List command
        list_parser = subparsers.add_parser("list", help="List available archives")
        list_parser.add_argument("--filter-tags", nargs="*", help="Filter by tags")
        list_parser.add_argument("--filter-author", help="Filter by author")
        list_parser.add_argument(
            "--sort-by",
            choices=["name", "date", "size"],
            default="date",
            help="Sort criteria",
        )

        # Preview command
        preview_parser = subparsers.add_parser(
            "preview", help="Preview archive contents"
        )
        preview_parser.add_argument("archive", help="Archive file path")
        preview_parser.add_argument(
            "--detailed", action="store_true", help="Show detailed information"
        )

        # Replay command
        replay_parser = subparsers.add_parser("replay", help="Replay agent decisions")
        replay_parser.add_argument("archive", help="Archive file path")
        replay_parser.add_argument(
            "--interactive",
            action="store_true",
            help="Start interactive debugging session",
        )
        replay_parser.add_argument(
            "--from-time", help="Start time for replay (ISO format)"
        )
        replay_parser.add_argument("--to-time", help="End time for replay (ISO format)")
        replay_parser.add_argument("--output", help="Export replay session to file")

        # Analyze command
        analyze_parser = subparsers.add_parser(
            "analyze", help="Analyze agent decision patterns"
        )
        analyze_parser.add_argument("archive", help="Archive file path")
        analyze_parser.add_argument(
            "--output-format",
            choices=["json", "text", "html"],
            default="text",
            help="Output format",
        )
        analyze_parser.add_argument(
            "--save-report", help="Save analysis report to file"
        )

        return parser

    def run(self, args: List[str] = None) -> int:
        """Run the CLI with given arguments"""
        if args is None:
            args = sys.argv[1:]

        parser = self.create_parser()
        parsed_args = parser.parse_args(args)

        if not parsed_args.command:
            parser.print_help()
            return 1

        try:
            if parsed_args.command == "export":
                return self.cmd_export(parsed_args)
            elif parsed_args.command == "import":
                return self.cmd_import(parsed_args)
            elif parsed_args.command == "merge":
                return self.cmd_merge(parsed_args)
            elif parsed_args.command == "list":
                return self.cmd_list(parsed_args)
            elif parsed_args.command == "preview":
                return self.cmd_preview(parsed_args)
            elif parsed_args.command == "replay":
                return self.cmd_replay(parsed_args)
            elif parsed_args.command == "analyze":
                return self.cmd_analyze(parsed_args)
            else:
                print(f"❌ Unknown command: {parsed_args.command}")
                return 1

        except Exception as e:
            print(f"❌ Command failed: {e}")
            return 1

    def cmd_export(self, args) -> int:
        """Handle export command"""
        print(f"[DISC] Exporting agent '{args.name}'...")

        # Try to find the agent instance
        # In a real implementation, this would integrate with the actual aetherra agent system
        # For now, we'll create a mock agent
        try:
            agent_instance = self._get_agent_instance(args.name)
            if agent_instance is None:
                print(f"❌ Agent '{args.name}' not found or not active")
                return 1

            # Export the agent
            archive_path = export_agent(
                agent_instance=agent_instance,
                name=args.name,
                version=args.version,
                description=args.description,
                tags=args.tags,
                privacy_level=args.privacy,
                archive_dir=args.output_dir,
            )

            print("✅ Agent exported successfully!")
            print(f"📁 Archive location: {archive_path}")
            print(f"🏷️  Tags: {', '.join(args.tags) if args.tags else 'None'}")
            print(f"🔒 Privacy: {args.privacy}")

            return 0

        except Exception as e:
            print(f"❌ Export failed: {e}")
            return 1

    def cmd_import(self, args) -> int:
        """Handle import command"""
        print(f"📥 Importing agent from '{args.archive}'...")

        try:
            archive_path = Path(args.archive)
            if not archive_path.exists():
                print(f"❌ Archive file not found: {args.archive}")
                return 1

            # Preview the archive first
            preview = self.importer.preview_archive(archive_path)
            agent_name = preview["metadata"]["name"]
            agent_version = preview["metadata"]["version"]

            print(f"📋 Importing agent: {agent_name} v{agent_version}")
            print(f"📊 Memories: {preview['cognitive_summary']['memory_items']}")
            print(f"🎯 Goals: {preview['cognitive_summary']['goal_count']}")

            # Get or create target agent
            target_agent_name = args.target_agent or agent_name
            target_agent = self._get_or_create_agent(target_agent_name)

            # Import the agent
            result = import_agent(archive_path, target_agent, args.merge_mode)

            print("✅ Agent imported successfully!")
            print(f"🎯 Target agent: {target_agent_name}")
            print(f"🔄 Merge mode: {args.merge_mode}")
            print("📈 Restoration results:")
            for component, success in result["restoration_results"].items():
                status = "✅" if success else "❌"
                print(f"  {status} {component}")

            return 0

        except Exception as e:
            print(f"❌ Import failed: {e}")
            return 1

    def cmd_merge(self, args) -> int:
        """Handle merge command"""
        print("🔀 Merging agents...")
        print(f"[DISC] Primary: {args.primary}")
        print(f"[DISC] Secondary: {args.secondary}")

        try:
            # Perform the merge
            output_path = merge_agents(
                primary_path=args.primary,
                secondary_path=args.secondary,
                output_path=args.output,
            )

            print("✅ Agents merged successfully!")
            print(f"📁 Merged archive: {output_path}")
            print(f"🧠 Strategy: {args.strategy}")

            return 0

        except Exception as e:
            print(f"❌ Merge failed: {e}")
            return 1

    def cmd_list(self, args) -> int:
        """Handle list command"""
        print("📚 Available agent archives:")

        try:
            archives = self.archiver.list_archives()

            if not archives:
                print("  No archives found.")
                return 0

            # Apply filters
            if args.filter_tags:
                archives = [
                    a
                    for a in archives
                    if any(tag in a.get("tags", []) for tag in args.filter_tags)
                ]

            if args.filter_author:
                archives = [
                    a for a in archives if args.filter_author in a.get("created_by", "")
                ]

            # Sort archives
            if args.sort_by == "name":
                archives.sort(key=lambda x: x.get("name", ""))
            elif args.sort_by == "date":
                archives.sort(key=lambda x: x.get("created_on_disk", ""), reverse=True)
            elif args.sort_by == "size":
                archives.sort(key=lambda x: x.get("file_size", 0), reverse=True)

            # Display archives
            for archive in archives:
                name = archive.get("name", "Unknown")
                version = archive.get("version", "?")
                size_mb = archive.get("file_size", 0) / (1024 * 1024)
                tags = ", ".join(archive.get("tags", []))
                created = archive.get("created_at", "Unknown")[:10]  # Date only

                print(f"  [DISC] {name} v{version}")
                print(f"     📏 Size: {size_mb:.1f} MB | 📅 {created}")
                if tags:
                    print(f"     🏷️  Tags: {tags}")
                print()

            print(f"Total: {len(archives)} archives")
            return 0

        except Exception as e:
            print(f"❌ List failed: {e}")
            return 1

    def cmd_preview(self, args) -> int:
        """Handle preview command"""
        print(f"👁️  Previewing archive: {args.archive}")

        try:
            preview = self.importer.preview_archive(Path(args.archive))
            metadata = preview["metadata"]
            summary = preview["cognitive_summary"]

            print("\n📋 Agent Information:")
            print(f"  Name: {metadata['name']}")
            print(f"  Version: {metadata['version']}")
            print(f"  Description: {metadata.get('description', 'No description')}")
            print(f"  Created: {metadata.get('created_at', 'Unknown')}")
            print(f"  Author: {metadata.get('created_by', 'Unknown')}")
            print(f"  Tags: {', '.join(metadata.get('tags', []))}")

            print("\n🧠 Cognitive State:")
            print(f"  Memory items: {summary['memory_items']}")
            print(f"  Goals: {summary['goal_count']}")
            print(f"  Pattern types: {len(summary['pattern_types'])}")
            print(f"  Has replay data: {'✅' if summary['has_replay_data'] else '❌'}")

            if args.detailed and summary["pattern_types"]:
                print(f"  Pattern types: {', '.join(summary['pattern_types'])}")

            print("\n📁 File Information:")
            print(f"  Size: {preview['file_info']['size_bytes'] / 1024:.1f} KB")
            print(f"  Created on disk: {preview['file_info']['created'][:19]}")

            compatibility = preview.get("compatibility", {})
            if compatibility:
                print("\n⚙️  Compatibility:")
                print(
                    f"  aetherra version: {compatibility.get('aetherra_version', 'Unknown')}"
                )
                if compatibility.get("required_plugins"):
                    print(
                        f"  Required plugins: {', '.join(compatibility['required_plugins'])}"
                    )

            return 0

        except Exception as e:
            print(f"❌ Preview failed: {e}")
            return 1

    def cmd_replay(self, args) -> int:
        """Handle replay command"""
        print(f"🎬 Starting replay session for: {args.archive}")

        try:
            # Load archive and extract replay data
            from .agent_importer import NSEReader

            archive_data = NSEReader.read_archive(Path(args.archive))

            replay_data = archive_data.get("replay_data", {})
            decision_traces = replay_data.get("decision_traces", [])

            if not decision_traces:
                print("❌ No replay data found in archive")
                return 1

            agent_name = archive_data["agent_metadata"]["name"]
            print(f"🎯 Agent: {agent_name}")
            print(f"📊 Decisions available: {len(decision_traces)}")

            # Filter by time range if specified
            filtered_traces = decision_traces
            if args.from_time or args.to_time:
                filtered_traces = self._filter_by_time_range(
                    decision_traces, args.from_time, args.to_time
                )
                print(f"🕒 Filtered to: {len(filtered_traces)} decisions")

            if args.interactive:
                # Start interactive debugging session
                debugger = InteractiveReplayDebugger(self.replay_engine)
                session_id = debugger.start_debug_session(agent_name, filtered_traces)

                print("\n🎮 Interactive Debug Mode")
                print("Enter commands (type 'help' for available commands):")

                while True:
                    try:
                        command_line = input("debug> ").strip()
                        if not command_line:
                            continue

                        if command_line.lower() in ["quit", "exit", "q"]:
                            break

                        parts = command_line.split()
                        command = parts[0]
                        args = parts[1:]

                        debugger.debug_command(command, *args)

                    except KeyboardInterrupt:
                        print("\n👋 Exiting debug session...")
                        break
                    except EOFError:
                        break

                self.replay_engine.end_session(session_id)

            else:
                # Non-interactive analysis
                session_id = self.replay_engine.start_replay_session(
                    agent_name, filtered_traces
                )
                analysis = self.replay_engine.analyze_session(session_id)

                print("\n📊 Replay Analysis:")
                print(f"  Total decisions: {analysis['total_decisions']}")

                if "confidence_stats" in analysis:
                    stats = analysis["confidence_stats"]
                    print(f"  Average confidence: {stats.get('average', 0):.2f}")
                    print(
                        f"  Low confidence decisions: {stats.get('low_confidence_count', 0)}"
                    )

                if "outcome_analysis" in analysis:
                    outcomes = analysis["outcome_analysis"]
                    success_rate = outcomes.get("success_rate", 0)
                    print(f"  Success rate: {success_rate:.1%}")

                if args.output:
                    export_path = self.replay_engine.export_session(
                        session_id, Path(args.output)
                    )
                    print(f"💾 Session exported to: {export_path}")

                self.replay_engine.end_session(session_id)

            return 0

        except Exception as e:
            print(f"❌ Replay failed: {e}")
            return 1

    def cmd_analyze(self, args) -> int:
        """Handle analyze command"""
        print(f"📈 Analyzing agent patterns: {args.archive}")

        try:
            # Load archive and run analysis
            from .agent_importer import NSEReader

            archive_data = NSEReader.read_archive(Path(args.archive))

            replay_data = archive_data.get("replay_data", {})
            decision_traces = replay_data.get("decision_traces", [])

            if not decision_traces:
                print("❌ No decision data found for analysis")
                return 1

            agent_name = archive_data["agent_metadata"]["name"]
            session_id = self.replay_engine.start_replay_session(
                agent_name, decision_traces
            )
            analysis = self.replay_engine.analyze_session(session_id)

            # Format output based on requested format
            if args.output_format == "json":
                output = json.dumps(analysis, indent=2, default=str)
                print(output)
            elif args.output_format == "text":
                self._format_analysis_text(analysis)
            elif args.output_format == "html":
                output = self._format_analysis_html(analysis)
                print(output)

            # Save report if requested
            if args.save_report:
                with open(args.save_report, "w") as f:
                    if args.output_format == "json":
                        json.dump(analysis, f, indent=2, default=str)
                    else:
                        f.write(output)
                print(f"💾 Analysis report saved to: {args.save_report}")

            self.replay_engine.end_session(session_id)
            return 0

        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            return 1

    def _get_agent_instance(self, agent_name: str):
        """Get active agent instance (mock implementation)"""

        # In a real implementation, this would interface with the aetherra agent system
        # For now, return a mock agent for demonstration
        class MockAgent:
            def __init__(self, name):
                self.agent_id = name
                self.memory_store = {"memories": [f"Experience with {name}"]}
                self.goals = {
                    "primary": "Help users",
                    "secondary": ["Learn continuously"],
                }

        return MockAgent(agent_name)

    def _get_or_create_agent(self, agent_name: str):
        """Get existing agent or create new one"""
        # Mock implementation - in reality, would interface with aetherra
        return self._get_agent_instance(agent_name)

    def _filter_by_time_range(
        self, traces: List[dict], from_time: Optional[str], to_time: Optional[str]
    ) -> List[dict]:
        """Filter decision traces by time range"""
        filtered = traces

        if from_time:
            from datetime import datetime

            from_dt = datetime.fromisoformat(from_time.replace("Z", "+00:00"))
            filtered = [
                t
                for t in filtered
                if datetime.fromisoformat(t.get("timestamp", "").replace("Z", "+00:00"))
                >= from_dt
            ]

        if to_time:
            from datetime import datetime

            to_dt = datetime.fromisoformat(to_time.replace("Z", "+00:00"))
            filtered = [
                t
                for t in filtered
                if datetime.fromisoformat(t.get("timestamp", "").replace("Z", "+00:00"))
                <= to_dt
            ]

        return filtered

    def _format_analysis_text(self, analysis: dict):
        """Format analysis as readable text"""
        print("\n📊 Decision Analysis Report")
        print("=" * 50)

        print("\n📈 Overview:")
        print(f"  Total decisions analyzed: {analysis.get('total_decisions', 0)}")

        if "time_span" in analysis:
            time_span = analysis["time_span"]
            print(f"  Time span: {time_span.get('duration_seconds', 0):.0f} seconds")
            print(
                f"  Decision rate: {time_span.get('decisions_per_minute', 0):.1f} per minute"
            )

        if "confidence_stats" in analysis:
            print("\n🎲 Confidence Analysis:")
            stats = analysis["confidence_stats"]
            print(f"  Average confidence: {stats.get('average', 0):.2f}")
            print(f"  Range: {stats.get('min', 0):.2f} - {stats.get('max', 0):.2f}")
            print(f"  Low confidence (<0.5): {stats.get('low_confidence_count', 0)}")
            print(f"  High confidence (>0.8): {stats.get('high_confidence_count', 0)}")

        if "outcome_analysis" in analysis:
            print("\n📊 Outcome Analysis:")
            outcomes = analysis["outcome_analysis"]
            success_rate = outcomes.get("success_rate", 0)
            failure_rate = outcomes.get("failure_rate", 0)
            print(f"  Success rate: {success_rate:.1%}")
            print(f"  Failure rate: {failure_rate:.1%}")

        if "decision_patterns" in analysis:
            patterns = analysis["decision_patterns"]

            if patterns.get("repeated_decisions"):
                print("\n🔄 Repeated Decisions:")
                for pattern in patterns["repeated_decisions"][:5]:  # Top 5
                    print(f"  {pattern['count']}x: {pattern['pattern'][:60]}...")

        if "reasoning_themes" in analysis:
            themes = analysis["reasoning_themes"]
            if themes:
                print("\n💭 Common Reasoning Themes:")
                for theme in themes[:5]:  # Top 5
                    print(f"  '{theme['theme']}' - {theme['frequency']} occurrences")

    def _format_analysis_html(self, analysis: dict) -> str:
        """Format analysis as HTML report"""
        html = f"""
        <html>
        <head><title>Agent Decision Analysis</title></head>
        <body>
        <h1>📊 Agent Decision Analysis Report</h1>
        <p>Total decisions: {analysis.get("total_decisions", 0)}</p>
        <!-- Add more HTML formatting here -->
        </body>
        </html>
        """
        return html


def main():
    """Main entry point for CLI"""
    cli = AgentArchiveCLI()
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())
