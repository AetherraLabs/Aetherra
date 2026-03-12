"""
Standalone test runner for Task 5: Orchestrator Framework.

Covers:
- IntentParser (20 tests)
- PlanGenerator (15 tests)
- CodeGenerationWorkflow (15 tests)
- CodeOrchestrator E2E flow (10 tests)

Run with:
    python test_orchestrator_task5_standalone.py
"""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from aetherra_coding.orchestrator import (
    CodeGenerationPlan,
    CodeGenerationWorkflow,
    CodeGenStep,
    CodeOrchestrator,
    IntentParser,
    ParsedIntent,
    PlanGenerator,
)


class TestIntentParser(unittest.TestCase):
    pass


def _intent_cases():
    return [
        ("parse_function_name", "Create a function factorial", "function", "factorial"),
        (
            "parse_function_with_to",
            "Create a function to normalize",
            "function",
            "normalize",
        ),
        ("parse_method", "Build method compute_score", "function", "compute_score"),
        ("parse_class", "Create class InvoiceManager", "class", "InvoiceManager"),
        ("parse_class_build", "build a class DataBridge", "class", "DataBridge"),
        ("parse_api_module", "Create API endpoints for users", "module", "api_module"),
        ("parse_default_module", "Refactor this code", "module", "generated_artifact"),
        (
            "detect_recursive_constraint",
            "Create function factorial recursive",
            "function",
            "factorial",
        ),
        ("detect_async_constraint", "Create function fetch async", "function", "fetch"),
        (
            "detect_error_handling_requirement",
            "Create function parse and handle errors",
            "function",
            "parse",
        ),
        (
            "detect_docstring_requirement",
            "Create function sum with docstring",
            "function",
            "sum",
        ),
        (
            "detect_tests_requirement",
            "Create function hash and test it",
            "function",
            "hash",
        ),
        ("detect_flask_dependency", "Create flask api route", "module", "api_module"),
        (
            "detect_fastapi_dependency",
            "Create fastapi endpoint",
            "module",
            "api_module",
        ),
        (
            "detect_pandas_dependency",
            "Create pandas data cleaner",
            "module",
            "generated_artifact",
        ),
        (
            "complexity_low",
            "Create simple quick helper function to trim",
            "function",
            "trim",
        ),
        (
            "complexity_high",
            "Create complex distributed scalable orchestrator",
            "module",
            "generated_artifact",
        ),
        ("complexity_medium", "Create function aggregate", "function", "aggregate"),
        ("empty_intent", "", "module", "generated_artifact"),
        ("whitespace_intent", "   ", "module", "generated_artifact"),
    ]


for case_name, intent, expected_type, expected_target in _intent_cases():

    def _make_test(
        _intent=intent, _expected_type=expected_type, _expected_target=expected_target
    ):
        def _test(self):
            parser = IntentParser()
            parsed = parser.parse(_intent)
            self.assertEqual(parsed.intent_type, _expected_type)
            self.assertEqual(parsed.target_name, _expected_target)
            self.assertIsInstance(parsed.requirements, list)
            self.assertIsInstance(parsed.constraints, list)
            self.assertIsInstance(parsed.dependencies, list)

        return _test

    setattr(TestIntentParser, f"test_{case_name}", _make_test())


class TestPlanGenerator(unittest.TestCase):
    pass


def _make_parsed(intent_type="function", target="do_work", complexity="medium"):
    return ParsedIntent(
        raw_intent=f"Create {intent_type} {target}",
        intent_type=intent_type,
        target_name=target,
        entities=[intent_type],
        requirements=["tests"],
        constraints=[],
        dependencies=[],
        complexity=complexity,
    )


def _plan_cases():
    return [
        ("default_target_file", _make_parsed(), None, "generated/do_work.py"),
        ("scope_target_file", _make_parsed(), ["src/custom.py"], "src/custom.py"),
        (
            "test_file_derivation",
            _make_parsed(target="alpha"),
            None,
            "generated/alpha.py",
        ),
        ("effort_low", _make_parsed(complexity="low"), None, "generated/do_work.py"),
        (
            "effort_medium",
            _make_parsed(complexity="medium"),
            None,
            "generated/do_work.py",
        ),
        ("effort_high", _make_parsed(complexity="high"), None, "generated/do_work.py"),
        ("steps_len", _make_parsed(), None, "generated/do_work.py"),
        ("steps_names_order", _make_parsed(), None, "generated/do_work.py"),
        ("steps_output_types", _make_parsed(), None, "generated/do_work.py"),
        (
            "parsed_intent_roundtrip",
            _make_parsed(target="beta"),
            None,
            "generated/beta.py",
        ),
        (
            "class_target_generation",
            _make_parsed(intent_type="class", target="Widget"),
            None,
            "generated/Widget.py",
        ),
        (
            "api_scope_preserved",
            _make_parsed(intent_type="module", target="api"),
            ["aetherra_hub/new_api.py"],
            "aetherra_hub/new_api.py",
        ),
        (
            "derive_test_file_custom_scope",
            _make_parsed(target="x"),
            ["pkg/mod.py"],
            "pkg/mod.py",
        ),
        ("plan_contains_tests_step", _make_parsed(), None, "generated/do_work.py"),
        ("plan_contains_docs_step", _make_parsed(), None, "generated/do_work.py"),
    ]


for case_name, parsed, scope, expected_target in _plan_cases():

    def _make_test(
        _parsed=parsed, _scope=scope, _expected_target=expected_target, _case=case_name
    ):
        def _test(self):
            gen = PlanGenerator()
            plan = gen.generate(_parsed, _scope)
            self.assertEqual(plan.target_file, _expected_target)
            self.assertEqual(plan.parsed_intent.target_name, _parsed.target_name)
            self.assertEqual(len(plan.steps), 5)
            if _case == "effort_low":
                self.assertEqual(plan.estimated_effort, "1-2h")
            if _case == "effort_medium":
                self.assertEqual(plan.estimated_effort, "3-5h")
            if _case == "effort_high":
                self.assertEqual(plan.estimated_effort, "6-10h")
            if _case == "steps_names_order":
                names = [s.name for s in plan.steps]
                self.assertEqual(
                    names, ["skeleton", "logic", "errors", "docs", "tests"]
                )
            if _case == "steps_output_types":
                outputs = [s.output_type for s in plan.steps]
                self.assertIn("tests", outputs)
                self.assertIn("docs", outputs)
            if _case == "derive_test_file_custom_scope":
                self.assertTrue(plan.test_file.endswith("test_mod.py"))
            if _case == "plan_contains_tests_step":
                self.assertTrue(any(s.name == "tests" for s in plan.steps))
            if _case == "plan_contains_docs_step":
                self.assertTrue(any(s.name == "docs" for s in plan.steps))

        return _test

    setattr(TestPlanGenerator, f"test_{case_name}", _make_test())


class TestCodeGenerationWorkflow(unittest.TestCase):
    pass


def _workflow_plan(parsed: ParsedIntent) -> CodeGenerationPlan:
    return CodeGenerationPlan(
        parsed_intent=parsed,
        steps=[
            CodeGenStep("skeleton", "Generate code skeleton", "code"),
            CodeGenStep("logic", "Add business logic", "code"),
            CodeGenStep("errors", "Add error handling", "code"),
            CodeGenStep("docs", "Add documentation", "docs"),
            CodeGenStep("tests", "Generate tests", "tests"),
        ],
        estimated_effort="3-5h",
        target_file=f"generated/{parsed.target_name}.py",
        test_file=f"tests/unit/test_{parsed.target_name}.py",
    )


def _workflow_cases():
    return [
        ("function_skeleton", _make_parsed(target="compute")),
        ("class_skeleton", _make_parsed(intent_type="class", target="MyClass")),
        (
            "async_skeleton",
            ParsedIntent(
                "Create function fetch async",
                "function",
                "fetch",
                constraints=["async"],
            ),
        ),
        ("factorial_logic", _make_parsed(target="factorial")),
        ("error_handling_added", _make_parsed(target="validate")),
        ("docs_generated", _make_parsed(target="docs_fn")),
        ("tests_generated", _make_parsed(target="test_fn")),
        ("execute_returns_generated_code", _make_parsed(target="pipe")),
        (
            "class_tests_reference_class",
            _make_parsed(intent_type="class", target="Widget"),
        ),
        ("function_tests_reference_function", _make_parsed(target="echo")),
        (
            "docs_include_constraints",
            ParsedIntent("x", "function", "x", constraints=["recursive"]),
        ),
        (
            "docs_include_dependencies",
            ParsedIntent("x", "function", "x", dependencies=["flask"]),
        ),
        (
            "recursive_constraint_preserved",
            ParsedIntent("x", "function", "factorial", constraints=["recursive"]),
        ),
        ("source_non_empty", _make_parsed(target="non_empty")),
        ("test_non_empty", _make_parsed(target="test_non_empty")),
    ]


for case_name, parsed in _workflow_cases():

    def _make_test(_parsed=parsed, _case=case_name):
        def _test(self):
            wf = CodeGenerationWorkflow()
            plan = _workflow_plan(_parsed)
            out = wf.execute(plan)
            self.assertTrue(out.source_code)
            self.assertTrue(out.test_code)
            self.assertTrue(out.docs)

            if _case == "function_skeleton":
                self.assertIn("def compute", out.source_code)
            if _case == "class_skeleton":
                self.assertIn("class MyClass", out.source_code)
            if _case == "async_skeleton":
                self.assertIn("async def fetch", out.source_code)
            if _case == "factorial_logic":
                self.assertIn("factorial(value - 1)", out.source_code)
            if _case == "error_handling_added":
                self.assertIn("raise ValueError", out.source_code)
            if _case == "docs_generated":
                self.assertIn("Intent type", out.docs)
            if _case == "tests_generated":
                self.assertIn("def test_", out.test_code)
            if _case == "class_tests_reference_class":
                self.assertIn("Widget", out.test_code)
            if _case == "function_tests_reference_function":
                self.assertIn("echo", out.test_code)
            if _case == "docs_include_constraints":
                self.assertIn("recursive", out.docs)
            if _case == "docs_include_dependencies":
                self.assertIn("flask", out.docs)
            if _case == "recursive_constraint_preserved":
                self.assertIn("factorial", out.source_code)
            if _case == "source_non_empty":
                self.assertGreater(len(out.source_code), 10)
            if _case == "test_non_empty":
                self.assertGreater(len(out.test_code), 10)

        return _test

    setattr(TestCodeGenerationWorkflow, f"test_{case_name}", _make_test())


class TestOrchestratorE2E(unittest.TestCase):
    pass


def _orchestrator_cases():
    return [
        (
            "plan_creates_steps",
            "Create function factorial recursively",
            ["generated/factorial.py"],
        ),
        ("plan_without_scope", "Create function add", None),
        (
            "generate_step0_dry_run",
            "Create function normalize",
            ["generated/normalize.py"],
        ),
        (
            "generate_invalid_step_index_raises",
            "Create function normalize",
            ["generated/normalize.py"],
        ),
        (
            "plan_stores_internal_parsed_intent",
            "Create function hash",
            ["generated/hash.py"],
        ),
        (
            "plan_sets_codegen_plan",
            "Create class ItemBuilder",
            ["generated/item_builder.py"],
        ),
        (
            "generate_for_new_file_contains_def",
            "Create function sanitize",
            ["generated/sanitize.py"],
        ),
        (
            "generate_summary_contains_target",
            "Create function clamp",
            ["generated/clamp.py"],
        ),
        (
            "plan_complexity_high",
            "Create complex distributed orchestrator",
            ["generated/complex_orch.py"],
        ),
        ("plan_logs_steps", "Create function logger", ["generated/logger.py"]),
    ]


for case_name, intent, scope in _orchestrator_cases():

    def _make_test(_intent=intent, _scope=scope, _case=case_name):
        def _test(self):
            with tempfile.TemporaryDirectory() as td:
                repo = Path(td)
                (repo / ".aetherra" / "rollback").mkdir(parents=True, exist_ok=True)
                orch = CodeOrchestrator(repo_root=repo)

                plan = orch.plan(_intent, scope=_scope)
                self.assertGreaterEqual(len(plan.steps), 1)

                if _case == "plan_without_scope":
                    self.assertTrue(
                        orch._codegen_plan.target_file.startswith("generated/")
                    )

                if _case == "generate_invalid_step_index_raises":
                    with self.assertRaises(IndexError):
                        orch.generate(999)
                    return

                patch = orch.generate(0, dry_run=True)
                self.assertFalse(patch.applied)
                self.assertTrue(patch.diff)

                if _case == "generate_step0_dry_run":
                    self.assertIn("***", patch.diff)
                if _case == "plan_stores_internal_parsed_intent":
                    self.assertIsNotNone(orch._parsed_intent)
                    self.assertEqual(orch._parsed_intent.intent_type, "function")
                if _case == "plan_sets_codegen_plan":
                    self.assertIsNotNone(orch._codegen_plan)
                if _case == "generate_for_new_file_contains_def":
                    self.assertIn("def sanitize", patch.diff)
                if _case == "generate_summary_contains_target":
                    self.assertIn("clamp.py", patch.summary)
                if _case == "plan_complexity_high":
                    self.assertEqual(orch._parsed_intent.complexity, "high")
                if _case == "plan_logs_steps":
                    self.assertTrue(
                        any("skeleton" in s.description for s in plan.steps)
                    )

        return _test

    setattr(TestOrchestratorE2E, f"test_{case_name}", _make_test())


if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    classes = [
        TestIntentParser,
        TestPlanGenerator,
        TestCodeGenerationWorkflow,
        TestOrchestratorE2E,
    ]

    for cls in classes:
        suite.addTests(loader.loadTestsFromTestCase(cls))

    total = suite.countTestCases()
    print(f"Running {total} Task 5 orchestrator tests...")
    print("=" * 60)

    result = unittest.TextTestRunner(verbosity=2).run(suite)

    print("=" * 60)
    passed = total - len(result.failures) - len(result.errors)
    print(f"Result: {passed}/{total} tests passed")

    sys.exit(0 if result.wasSuccessful() else 1)
