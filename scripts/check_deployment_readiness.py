#!/usr/bin/env python3
"""
Aetherra CI/CD Deployment Readiness Script
==========================================

This script validates that the Aetherra project is ready for CI/CD deployment
by checking all prerequisites, configurations, and system health.
"""

import json
import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DeploymentReadinessChecker:
    """Comprehensive deployment readiness validation"""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "checks": {},
            "summary": {
                "total_checks": 0,
                "passed": 0,
                "warnings": 0,
                "failures": 0,
                "deployment_ready": False,
            },
            "recommendations": [],
        }

    def check_file_structure(self) -> Dict[str, any]:
        """Check if required file structure exists"""
        logger.info("Checking file structure...")

        required_files = [
            ".github/workflows/ci.yml",
            ".github/workflows/app-deploy.yml",
            ".github/workflows/monitoring.yml",
            "requirements/base.txt",
            "requirements/dev.txt",
            "pyproject.toml",
            "tests/conftest.py",
            "Dockerfile",
            ".pre-commit-config.yaml",
            "scripts/cleanup_project.py",
        ]

        required_dirs = ["src", "tests", "requirements", ".github/workflows", "scripts"]

        missing_files = []
        missing_dirs = []

        for file_path in required_files:
            if not (self.project_root / file_path).exists():
                missing_files.append(file_path)

        for dir_path in required_dirs:
            if not (self.project_root / dir_path).exists():
                missing_dirs.append(dir_path)

        result = {
            "status": "pass" if not missing_files and not missing_dirs else "fail",
            "missing_files": missing_files,
            "missing_directories": missing_dirs,
            "message": "All required files and directories present"
            if not missing_files and not missing_dirs
            else f"Missing {len(missing_files)} files and {len(missing_dirs)} directories",
        }

        return result

    def check_github_actions(self) -> Dict[str, any]:
        """Validate GitHub Actions workflows"""
        logger.info("Checking GitHub Actions workflows...")

        workflows_dir = self.project_root / ".github" / "workflows"

        if not workflows_dir.exists():
            return {
                "status": "fail",
                "message": "GitHub Actions workflows directory not found",
            }

        workflow_files = list(workflows_dir.glob("*.yml"))

        if len(workflow_files) < 3:
            return {
                "status": "warning",
                "message": f"Only {len(workflow_files)} workflow files found, expected at least 3",
                "workflows": [f.name for f in workflow_files],
            }

        return {
            "status": "pass",
            "message": f"Found {len(workflow_files)} workflow files",
            "workflows": [f.name for f in workflow_files],
        }

    def check_requirements(self) -> Dict[str, any]:
        """Validate requirements files"""
        logger.info("Checking requirements configuration...")

        requirements_dir = self.project_root / "requirements"

        if not requirements_dir.exists():
            return {"status": "fail", "message": "Requirements directory not found"}

        required_req_files = ["base.txt", "dev.txt"]
        missing_req_files = []

        for req_file in required_req_files:
            if not (requirements_dir / req_file).exists():
                missing_req_files.append(req_file)

        if missing_req_files:
            return {
                "status": "fail",
                "message": f"Missing requirements files: {missing_req_files}",
            }

        # Check if files have content
        empty_files = []
        for req_file in required_req_files:
            file_path = requirements_dir / req_file
            try:
                if file_path.stat().st_size == 0:
                    empty_files.append(req_file)
            except:
                empty_files.append(req_file)

        if empty_files:
            return {
                "status": "warning",
                "message": f"Empty requirements files: {empty_files}",
            }

        return {
            "status": "pass",
            "message": "All requirements files present and non-empty",
        }

    def check_test_configuration(self) -> Dict[str, any]:
        """Validate test configuration"""
        logger.info("Checking test configuration...")

        tests_dir = self.project_root / "tests"

        if not tests_dir.exists():
            return {"status": "fail", "message": "Tests directory not found"}

        # Check for conftest.py
        if not (tests_dir / "conftest.py").exists():
            return {
                "status": "fail",
                "message": "conftest.py not found in tests directory",
            }

        # Check for pyproject.toml with pytest config
        pyproject_path = self.project_root / "pyproject.toml"
        if not pyproject_path.exists():
            return {
                "status": "warning",
                "message": "pyproject.toml not found - pytest configuration may be missing",
            }

        # Count test files
        test_files = list(tests_dir.glob("**/test_*.py")) + list(
            tests_dir.glob("**/*_test.py")
        )

        return {
            "status": "pass",
            "message": f"Test configuration valid with {len(test_files)} test files",
            "test_files_count": len(test_files),
        }

    def check_docker_configuration(self) -> Dict[str, any]:
        """Validate Docker configuration"""
        logger.info("Checking Docker configuration...")

        dockerfile_path = self.project_root / "Dockerfile"

        if not dockerfile_path.exists():
            return {"status": "fail", "message": "Dockerfile not found"}

        try:
            with open(dockerfile_path, "r") as f:
                dockerfile_content = f.read()

            # Check for multi-stage build
            if "FROM" not in dockerfile_content:
                return {
                    "status": "fail",
                    "message": "Invalid Dockerfile - no FROM instruction",
                }

            # Check for common Docker best practices
            best_practices = {
                "COPY requirements": "COPY requirements" in dockerfile_content,
                "RUN pip install": "pip install" in dockerfile_content,
                "WORKDIR": "WORKDIR" in dockerfile_content,
                "EXPOSE": "EXPOSE" in dockerfile_content or "CMD" in dockerfile_content,
            }

            missing_practices = [
                practice for practice, present in best_practices.items() if not present
            ]

            if missing_practices:
                return {
                    "status": "warning",
                    "message": f"Dockerfile may be missing best practices: {missing_practices}",
                }

            return {"status": "pass", "message": "Dockerfile configuration looks good"}

        except Exception as e:
            return {"status": "fail", "message": f"Error reading Dockerfile: {e}"}

    def check_code_quality_tools(self) -> Dict[str, any]:
        """Check code quality tool configuration"""
        logger.info("Checking code quality tools...")

        quality_files = {
            ".pre-commit-config.yaml": "Pre-commit hooks",
            "pyproject.toml": "Project configuration",
        }

        missing_files = []
        for file_path, description in quality_files.items():
            if not (self.project_root / file_path).exists():
                missing_files.append(f"{file_path} ({description})")

        if missing_files:
            return {
                "status": "warning",
                "message": f"Missing code quality files: {missing_files}",
            }

        return {"status": "pass", "message": "Code quality tools configured"}

    def check_project_cleanup(self) -> Dict[str, any]:
        """Check if project cleanup has been performed"""
        logger.info("Checking project cleanup status...")

        # Check for cleanup script
        cleanup_script = self.project_root / "scripts" / "cleanup_project.py"
        if not cleanup_script.exists():
            return {"status": "warning", "message": "Cleanup script not found"}

        # Check for cleanup report
        cleanup_report = self.project_root / "cleanup_report.json"
        if not cleanup_report.exists():
            return {
                "status": "warning",
                "message": "Project cleanup not yet performed - run cleanup script first",
            }

        try:
            with open(cleanup_report, "r") as f:
                report_data = json.load(f)

            # Check if cleanup was actually executed (not just dry run)
            if report_data.get("dry_run", True):
                return {
                    "status": "warning",
                    "message": "Cleanup was only performed as dry run - consider running actual cleanup",
                }

            return {"status": "pass", "message": "Project cleanup completed"}

        except Exception as e:
            return {
                "status": "warning",
                "message": f"Error reading cleanup report: {e}",
            }

    def check_environment_variables(self) -> Dict[str, any]:
        """Check for required environment variables in CI configuration"""
        logger.info("Checking environment variables...")

        # This would typically check CI workflow files for required secrets
        ci_workflow = self.project_root / ".github" / "workflows" / "ci.yml"

        if not ci_workflow.exists():
            return {"status": "fail", "message": "CI workflow file not found"}

        try:
            with open(ci_workflow, "r", encoding="utf-8", errors="ignore") as f:
                ci_content = f.read()

            # Check for secrets usage
            has_secrets = "secrets." in ci_content or "${{ secrets." in ci_content

            return {
                "status": "pass" if has_secrets else "warning",
                "message": "Environment variables configured"
                if has_secrets
                else "No secrets found in CI workflow",
            }

        except Exception as e:
            return {"status": "warning", "message": f"Error reading CI workflow: {e}"}

    def check_documentation(self) -> Dict[str, any]:
        """Check for essential documentation"""
        logger.info("Checking documentation...")

        doc_files = [
            "README.md",
            "LICENSE",
        ]

        missing_docs = []
        for doc_file in doc_files:
            if not (self.project_root / doc_file).exists():
                missing_docs.append(doc_file)

        # Check for generated documentation
        generated_docs = []
        potential_doc_files = [
            "LAUNCHER_USER_GUIDE.md",
            "MEMORY_ANALYTICS_DASHBOARD_DOCUMENTATION.md",
            "LYRIXA_SELF_EXTENDING_GUI_SYSTEM.md",
        ]

        for doc_file in potential_doc_files:
            if (self.project_root / doc_file).exists():
                generated_docs.append(doc_file)

        if missing_docs:
            return {
                "status": "warning",
                "message": f"Missing documentation: {missing_docs}",
                "generated_docs": generated_docs,
            }

        return {
            "status": "pass",
            "message": f"Documentation present, {len(generated_docs)} additional docs found",
            "generated_docs": generated_docs,
        }

    def check_security_configuration(self) -> Dict[str, any]:
        """Check security-related configurations"""
        logger.info("Checking security configuration...")

        security_issues = []

        # Check for .gitignore
        gitignore_path = self.project_root / ".gitignore"
        if not gitignore_path.exists():
            security_issues.append("No .gitignore file found")
        else:
            try:
                with open(gitignore_path, "r") as f:
                    gitignore_content = f.read().lower()

                security_patterns = [
                    "*.env",
                    "*.key",
                    "*.pem",
                    "secrets",
                    ".venv",
                    "__pycache__",
                ]

                missing_patterns = []
                for pattern in security_patterns:
                    if pattern not in gitignore_content:
                        missing_patterns.append(pattern)

                if missing_patterns:
                    security_issues.append(
                        f"Missing .gitignore patterns: {missing_patterns}"
                    )

            except Exception as e:
                security_issues.append(f"Error reading .gitignore: {e}")

        # Check for secrets in workflow files
        workflow_files = list(
            (self.project_root / ".github" / "workflows").glob("*.yml")
        )
        hardcoded_secrets = []

        for workflow_file in workflow_files:
            try:
                with open(workflow_file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read().lower()

                # Simple check for potential hardcoded secrets
                if (
                    any(
                        keyword in content
                        for keyword in ["password:", "token:", "key:", "secret:"]
                    )
                    and "secrets." not in content
                ):
                    hardcoded_secrets.append(workflow_file.name)

            except Exception:
                pass

        if hardcoded_secrets:
            security_issues.append(
                f"Potential hardcoded secrets in: {hardcoded_secrets}"
            )

        if security_issues:
            return {
                "status": "warning",
                "message": f"Security issues found: {security_issues}",
                "issues": security_issues,
            }

        return {"status": "pass", "message": "Security configuration looks good"}

    def run_all_checks(self) -> Dict[str, any]:
        """Run all deployment readiness checks"""
        logger.info("Starting deployment readiness checks...")

        checks = {
            "file_structure": self.check_file_structure,
            "github_actions": self.check_github_actions,
            "requirements": self.check_requirements,
            "test_configuration": self.check_test_configuration,
            "docker_configuration": self.check_docker_configuration,
            "code_quality_tools": self.check_code_quality_tools,
            "project_cleanup": self.check_project_cleanup,
            "environment_variables": self.check_environment_variables,
            "documentation": self.check_documentation,
            "security_configuration": self.check_security_configuration,
        }

        for check_name, check_function in checks.items():
            try:
                logger.info(f"Running check: {check_name}")
                result = check_function()
                self.results["checks"][check_name] = result

                # Update summary
                self.results["summary"]["total_checks"] += 1

                if result["status"] == "pass":
                    self.results["summary"]["passed"] += 1
                elif result["status"] == "warning":
                    self.results["summary"]["warnings"] += 1
                else:
                    self.results["summary"]["failures"] += 1

            except Exception as e:
                logger.error(f"Error in check {check_name}: {e}")
                self.results["checks"][check_name] = {
                    "status": "fail",
                    "message": f"Check failed with error: {e}",
                }
                self.results["summary"]["failures"] += 1
                self.results["summary"]["total_checks"] += 1

        # Determine overall deployment readiness
        self.results["summary"]["deployment_ready"] = (
            self.results["summary"]["failures"] == 0
            and self.results["summary"]["warnings"] <= 2
        )

        # Generate recommendations
        self._generate_recommendations()

        return self.results

    def _generate_recommendations(self) -> None:
        """Generate deployment recommendations based on check results"""
        recommendations = []

        for check_name, result in self.results["checks"].items():
            if result["status"] == "fail":
                recommendations.append(
                    f"CRITICAL: Fix {check_name} - {result['message']}"
                )
            elif result["status"] == "warning":
                recommendations.append(
                    f"RECOMMENDED: Address {check_name} - {result['message']}"
                )

        # General recommendations
        if self.results["summary"]["failures"] > 0:
            recommendations.append("Address all critical failures before deployment")

        if self.results["summary"]["warnings"] > 3:
            recommendations.append(
                "Consider addressing warnings to improve deployment reliability"
            )

        if self.results["summary"]["deployment_ready"]:
            recommendations.append("✅ Project appears ready for CI/CD deployment!")
        else:
            recommendations.append(
                "❌ Project needs additional work before CI/CD deployment"
            )

        self.results["recommendations"] = recommendations

    def save_report(self, filename: str = "deployment_readiness_report.json") -> Path:
        """Save deployment readiness report"""
        report_path = self.project_root / filename

        with open(report_path, "w") as f:
            json.dump(self.results, f, indent=2)

        logger.info(f"Deployment readiness report saved to: {report_path}")
        return report_path

    def print_summary(self) -> None:
        """Print deployment readiness summary"""
        print("\n" + "=" * 60)
        print("AETHERRA CI/CD DEPLOYMENT READINESS REPORT")
        print("=" * 60)

        print(f"\nProject: {self.project_root}")
        print(f"Timestamp: {self.results['timestamp']}")

        print(f"\nSummary:")
        print(f"  Total Checks: {self.results['summary']['total_checks']}")
        print(f"  ✅ Passed: {self.results['summary']['passed']}")
        print(f"  ⚠️  Warnings: {self.results['summary']['warnings']}")
        print(f"  ❌ Failures: {self.results['summary']['failures']}")
        print(
            f"  🚀 Deployment Ready: {'YES' if self.results['summary']['deployment_ready'] else 'NO'}"
        )

        print(f"\nCheck Results:")
        for check_name, result in self.results["checks"].items():
            status_icon = {"pass": "✅", "warning": "⚠️ ", "fail": "❌"}.get(
                result["status"], "❓"
            )

            print(f"  {status_icon} {check_name}: {result['message']}")

        if self.results["recommendations"]:
            print(f"\nRecommendations:")
            for rec in self.results["recommendations"]:
                print(f"  • {rec}")

        print("\n" + "=" * 60)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Aetherra CI/CD Deployment Readiness Checker"
    )
    parser.add_argument(
        "project_root",
        nargs="?",
        default=".",
        help="Path to Aetherra project root (default: current directory)",
    )
    parser.add_argument(
        "--save-report", action="store_true", help="Save detailed report to JSON file"
    )

    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()

    if not project_root.exists():
        print(f"Error: Project root does not exist: {project_root}")
        sys.exit(1)

    print("Aetherra CI/CD Deployment Readiness Checker")
    print(f"Analyzing project: {project_root}")

    checker = DeploymentReadinessChecker(project_root)
    results = checker.run_all_checks()

    if args.save_report:
        checker.save_report()

    checker.print_summary()

    # Exit with appropriate code
    if results["summary"]["deployment_ready"]:
        print("\n🎉 Project is ready for CI/CD deployment!")
        sys.exit(0)
    else:
        print("\n⚠️  Project needs additional work before deployment.")
        sys.exit(1)


if __name__ == "__main__":
    main()
