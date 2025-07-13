#!/usr/bin/env python3
"""
🤖 SELF-IMPROVEMENT TRIGGER SYSTEM
=================================

Automatically schedules and executes plugin improvement analysis.
Part of Lyrixa's autonomous self-improvement capabilities.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import schedule

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from .conversation_manager import LyrixaConversationManager
    from .plugin_diff_engine import ImprovementProposal, PluginDiffEngine

    COMPONENTS_AVAILABLE = True
except ImportError:
    logger.warning("⚠️ Some components not available for self-improvement system")
    COMPONENTS_AVAILABLE = False


class SelfImprovementScheduler:
    """
    🤖 Self-Improvement Scheduler

    Manages periodic plugin analysis and improvement generation
    without requiring user prompts.
    """

    def __init__(self, workspace_path: str, gui_interface=None):
        self.workspace_path = Path(workspace_path)
        self.gui_interface = gui_interface
        self.diff_engine = None
        self.conversation_manager = None

        # Configuration
        self.check_interval_hours = 24  # Check every 24 hours
        self.improvement_history_file = self.workspace_path / "improvement_history.json"
        self.analysis_results_file = self.workspace_path / "latest_analysis.json"

        # State tracking
        self.last_check_time = None
        self.improvement_history = []
        self.is_running = False
        self.background_task = None

        # Initialize components if available
        if COMPONENTS_AVAILABLE:
            self.diff_engine = PluginDiffEngine(str(workspace_path))
            self.conversation_manager = LyrixaConversationManager(
                workspace_path=str(workspace_path), gui_interface=gui_interface
            )

    def start_background_monitoring(self):
        """Start the background improvement monitoring system"""
        if self.is_running:
            logger.info("🤖 Self-improvement monitoring already running")
            return

        self.is_running = True
        self.background_task = asyncio.create_task(self._monitoring_loop())
        logger.info("🚀 Self-improvement monitoring started")
        logger.info(f"⏰ Will check plugins every {self.check_interval_hours} hours")

    def stop_background_monitoring(self):
        """Stop the background improvement monitoring system"""
        self.is_running = False
        if self.background_task:
            self.background_task.cancel()
        logger.info("⏹️ Self-improvement monitoring stopped")

    async def _monitoring_loop(self):
        """Main monitoring loop that runs in the background"""
        try:
            while self.is_running:
                try:
                    # Check if it's time for analysis
                    if self._should_run_analysis():
                        logger.info("🔍 Time for scheduled plugin analysis...")
                        await self.run_scheduled_analysis()

                    # Sleep for a reasonable check interval (1 hour)
                    await asyncio.sleep(3600)  # Check every hour

                except Exception as e:
                    logger.error(f"❌ Error in monitoring loop: {e}")
                    await asyncio.sleep(3600)  # Continue after error

        except asyncio.CancelledError:
            logger.info("🛑 Monitoring loop cancelled")

    def _should_run_analysis(self) -> bool:
        """Determine if it's time to run plugin analysis"""
        if self.last_check_time is None:
            return True  # First run

        time_since_last = datetime.now() - self.last_check_time
        return time_since_last >= timedelta(hours=self.check_interval_hours)

    async def run_scheduled_analysis(self):
        """Run the complete scheduled analysis and improvement process"""
        start_time = datetime.now()
        logger.info("🔧 Starting scheduled plugin improvement analysis...")

        try:
            # Step 1: Analyze all plugins
            analyses = await self.diff_engine.analyze_all_plugins()
            logger.info(f"📊 Analyzed {len(analyses)} plugins")

            # Step 2: Generate improvement proposals
            proposals = []
            for analysis in analyses:
                proposal = self.diff_engine.generate_improvement_proposal(analysis)
                if proposal:
                    proposals.append(proposal)

            logger.info(f"💡 Generated {len(proposals)} improvement proposals")

            # Step 3: Process proposals
            await self._process_improvement_proposals(proposals)

            # Step 4: Save results
            self._save_analysis_results(analyses, proposals)

            # Update last check time
            self.last_check_time = start_time

            # Step 5: Generate summary report
            summary = self._generate_improvement_summary(analyses, proposals)
            logger.info("📋 Analysis Summary:")
            logger.info(f"   Total plugins: {summary['total_plugins']}")
            logger.info(f"   Proposals generated: {summary['proposals_generated']}")
            logger.info(f"   Auto-applied: {summary['auto_applied']}")
            logger.info(f"   Pending review: {summary['pending_review']}")

        except Exception as e:
            logger.error(f"❌ Scheduled analysis failed: {e}")

    async def _process_improvement_proposals(
        self, proposals: List[ImprovementProposal]
    ):
        """Process improvement proposals - auto-apply or queue for review"""
        auto_applied = 0
        queued_for_review = 0

        for proposal in proposals:
            try:
                if proposal.auto_apply and proposal.risk_level == "low":
                    # Auto-apply low-risk improvements
                    success = await self._auto_apply_improvement(proposal)
                    if success:
                        auto_applied += 1
                        logger.info(
                            f"✅ Auto-applied improvement to {proposal.plugin_id}"
                        )
                    else:
                        # Failed to auto-apply, queue for review
                        await self._queue_for_review(proposal)
                        queued_for_review += 1
                else:
                    # Queue for manual review
                    await self._queue_for_review(proposal)
                    queued_for_review += 1

            except Exception as e:
                logger.error(
                    f"❌ Failed to process proposal for {proposal.plugin_id}: {e}"
                )

        if auto_applied > 0:
            logger.info(f"🤖 Auto-applied {auto_applied} low-risk improvements")
        if queued_for_review > 0:
            logger.info(f"📋 Queued {queued_for_review} proposals for manual review")

    async def _auto_apply_improvement(self, proposal: ImprovementProposal) -> bool:
        """Automatically apply a low-risk improvement"""
        try:
            # For now, we don't actually modify files automatically
            # This is a safety measure - all changes should be reviewed
            # In the future, this could implement very safe changes like adding comments

            logger.info(f"🔄 Would auto-apply: {proposal.proposed_change}")
            logger.info(f"   Plugin: {proposal.plugin_id}")
            logger.info(f"   Risk: {proposal.risk_level}")

            # Record the proposal but don't apply it
            self.improvement_history.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "plugin_id": proposal.plugin_id,
                    "action": "auto_apply_simulated",
                    "proposal": proposal.to_dict(),
                }
            )

            return False  # Always return False for safety

        except Exception as e:
            logger.error(f"❌ Auto-apply failed for {proposal.plugin_id}: {e}")
            return False

    async def _queue_for_review(self, proposal: ImprovementProposal):
        """Queue an improvement proposal for manual review"""
        try:
            # If GUI interface is available, inject into Plugin Editor
            if self.gui_interface and hasattr(self.gui_interface, "inject_plugin_code"):
                # Generate a review message for Lyrixa
                review_message = self._generate_review_message(proposal)

                # Use conversation manager to create a natural response
                if self.conversation_manager:
                    lyrixa_response = await self._generate_lyrixa_improvement_message(
                        proposal
                    )

                    # The conversation manager will detect this and trigger GUI injection
                    self.conversation_manager.handle_llm_response(lyrixa_response)

                logger.info(f"📋 Queued {proposal.plugin_id} for GUI review")
            else:
                # Save to file for later review
                proposal_file = (
                    self.workspace_path
                    / f"proposal_{proposal.plugin_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                )
                with open(proposal_file, "w") as f:
                    json.dump(proposal.to_dict(), f, indent=2)

                logger.info(
                    f"💾 Saved proposal for {proposal.plugin_id} to {proposal_file}"
                )

            # Record in history
            self.improvement_history.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "plugin_id": proposal.plugin_id,
                    "action": "queued_for_review",
                    "proposal": proposal.to_dict(),
                }
            )

        except Exception as e:
            logger.error(f"❌ Failed to queue proposal for {proposal.plugin_id}: {e}")

    def _generate_review_message(self, proposal: ImprovementProposal) -> str:
        """Generate a review message for the user"""
        return f"""
🔧 Plugin Improvement Suggestion

Plugin: {proposal.plugin_id}
Proposed Change: {proposal.proposed_change}
Impact: {proposal.impact}
Risk Level: {proposal.risk_level}
Confidence: {proposal.confidence:.2f}

Reasoning: {proposal.reasoning}

Would you like to review and apply this improvement?
"""

    async def _generate_lyrixa_improvement_message(
        self, proposal: ImprovementProposal
    ) -> str:
        """Generate a natural Lyrixa message about the improvement"""
        return f"""
I found a possible improvement to the {proposal.plugin_id} plugin. Let me inject the suggested changes into the Plugin Editor for your review:

```python
{proposal.suggested_code}
```

This improvement will {proposal.impact.lower()}. The change involves: {proposal.proposed_change}

Risk level: {proposal.risk_level}
My confidence: {proposal.confidence:.1%}

Reasoning: {proposal.reasoning}

I've loaded this into your Plugin Editor. You can review the changes and decide whether to save them using the Save button in the interface.
"""

    def _save_analysis_results(self, analyses, proposals):
        """Save analysis results to files"""
        # Save latest analysis
        analysis_data = {
            "timestamp": datetime.now().isoformat(),
            "analyses": [a.to_dict() for a in analyses],
            "proposals": [p.to_dict() for p in proposals],
        }

        with open(self.analysis_results_file, "w") as f:
            json.dump(analysis_data, f, indent=2)

        # Save improvement history
        with open(self.improvement_history_file, "w") as f:
            json.dump(self.improvement_history, f, indent=2)

        logger.info(f"💾 Analysis results saved to {self.analysis_results_file}")

    def _generate_improvement_summary(self, analyses, proposals) -> Dict[str, Any]:
        """Generate summary statistics"""
        return {
            "total_plugins": len(analyses),
            "proposals_generated": len(proposals),
            "auto_applied": len([p for p in proposals if p.auto_apply]),
            "pending_review": len([p for p in proposals if not p.auto_apply]),
            "average_confidence": sum(a.confidence_score for a in analyses)
            / len(analyses)
            if analyses
            else 0,
            "plugins_needing_improvement": len(
                [a for a in analyses if a.confidence_score < 0.7]
            ),
        }

    def get_improvement_status(self) -> Dict[str, Any]:
        """Get current improvement system status"""
        return {
            "is_running": self.is_running,
            "last_check_time": self.last_check_time.isoformat()
            if self.last_check_time
            else None,
            "check_interval_hours": self.check_interval_hours,
            "total_improvements_tracked": len(self.improvement_history),
            "components_available": COMPONENTS_AVAILABLE,
        }

    def force_analysis_now(self):
        """Force an immediate analysis (for testing/manual trigger)"""
        logger.info("🚀 Forcing immediate plugin analysis...")
        asyncio.create_task(self.run_scheduled_analysis())

    def set_check_interval(self, hours: int):
        """Update the check interval"""
        self.check_interval_hours = max(1, hours)  # Minimum 1 hour
        logger.info(f"⏰ Check interval updated to {self.check_interval_hours} hours")


class ImprovementQueue:
    """Manages queued improvements and user interactions"""

    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.queue_file = self.workspace_path / "improvement_queue.json"
        self.queue = []
        self.load_queue()

    def load_queue(self):
        """Load improvement queue from file"""
        if self.queue_file.exists():
            with open(self.queue_file, "r") as f:
                self.queue = json.load(f)

    def save_queue(self):
        """Save improvement queue to file"""
        with open(self.queue_file, "w") as f:
            json.dump(self.queue, f, indent=2)

    def add_proposal(self, proposal: ImprovementProposal):
        """Add a proposal to the queue"""
        self.queue.append(
            {
                "id": f"{proposal.plugin_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "proposal": proposal.to_dict(),
                "status": "pending",
                "created_at": datetime.now().isoformat(),
            }
        )
        self.save_queue()

    def get_pending_proposals(self) -> List[Dict]:
        """Get all pending proposals"""
        return [item for item in self.queue if item["status"] == "pending"]

    def approve_proposal(self, proposal_id: str):
        """Mark a proposal as approved"""
        for item in self.queue:
            if item["id"] == proposal_id:
                item["status"] = "approved"
                item["approved_at"] = datetime.now().isoformat()
                break
        self.save_queue()

    def reject_proposal(self, proposal_id: str, reason: str = ""):
        """Mark a proposal as rejected"""
        for item in self.queue:
            if item["id"] == proposal_id:
                item["status"] = "rejected"
                item["rejected_at"] = datetime.now().isoformat()
                item["rejection_reason"] = reason
                break
        self.save_queue()


# Example usage and testing
if __name__ == "__main__":

    async def main():
        print("🤖 Self-Improvement Trigger System Test")
        print("=" * 40)

        # Initialize the scheduler
        workspace_path = Path(__file__).parent.parent
        scheduler = SelfImprovementScheduler(str(workspace_path))

        # Check system status
        status = scheduler.get_improvement_status()
        print(f"📊 System Status:")
        print(f"   Components available: {status['components_available']}")
        print(f"   Running: {status['is_running']}")
        print(f"   Check interval: {status['check_interval_hours']} hours")

        # Run immediate analysis for testing
        if COMPONENTS_AVAILABLE:
            print("🚀 Running test analysis...")
            await scheduler.run_scheduled_analysis()
            print("✅ Test analysis complete")
        else:
            print("⚠️ Components not available - skipping analysis")

        print("🎉 Self-improvement system test complete!")

    asyncio.run(main())
