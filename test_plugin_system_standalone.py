"""
Standalone test runner for Task 3: Plugin System
Tests: plugin_processors.py, plugin_metadata_registry.py, plugin_wizard_backend.py

Run with:
    python test_plugin_system_standalone.py
"""

import io
import json
import sys
import os
import tempfile
import unittest

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Aetherra.plugins.core.plugin_processors import (
    ProcessConfig,
    ProcessResult,
    JSONProcessor,
    CSVProcessor,
    TextProcessor,
)
from Aetherra.plugins.core.plugin_metadata_registry import (
    PluginMetadataRecord,
    PluginRegistryManager,
    RegistrySearchResult,
)
from Aetherra.plugins.core.plugin_wizard_backend import (
    PluginWizardBackend,
    WizardResult,
    WizardValidationError,
    ValidationError,
    _to_class_name,
)


# ──────────────────────────────────────────────────────────────────────────────
# JSONProcessor tests (10 tests)
# ──────────────────────────────────────────────────────────────────────────────

class TestJSONProcessor(unittest.TestCase):

    def setUp(self):
        self.processor = JSONProcessor()

    # ── parse ─────────────────────────────────────────────────────────────────

    def test_parse_valid_dict(self):
        data = self.processor.parse('{"key": "value", "num": 42}')
        self.assertEqual(data["key"], "value")
        self.assertEqual(data["num"], 42)

    def test_parse_valid_list(self):
        data = self.processor.parse('[{"id": 1}, {"id": 2}]')
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)

    def test_parse_invalid_json_returns_error(self):
        result = self.processor.run("not json", ProcessConfig())
        self.assertFalse(result.success)
        self.assertIn("json", result.error.lower())

    # ── schema validation ─────────────────────────────────────────────────────

    def test_schema_validation_pass(self):
        data = [{"name": "Alice", "age": 30}]
        schema = {"required": ["name", "age"]}
        errors = self.processor.validate_schema(data, schema)
        self.assertEqual(errors, [])

    def test_schema_validation_fail_missing_field(self):
        data = [{"name": "Alice"}]
        schema = {"required": ["name", "age"]}
        errors = self.processor.validate_schema(data, schema)
        self.assertGreater(len(errors), 0)

    # ── filter ────────────────────────────────────────────────────────────────

    def test_filter_by_callable(self):
        data = [{"age": 25}, {"age": 40}, {"age": 18}]
        filtered = self.processor.filter(data, lambda r: r["age"] >= 25)
        self.assertEqual(len(filtered), 2)

    # ── transform ─────────────────────────────────────────────────────────────

    def test_transform(self):
        data = [{"x": 1}, {"x": 2}]
        result = self.processor.transform(data, lambda item: {"y": item["x"] * 2})
        self.assertEqual(result[0]["y"], 2)

    # ── export ────────────────────────────────────────────────────────────────

    def test_export_json(self):
        data = {"key": "value"}
        output = self.processor.export(data, "json")
        parsed = json.loads(output)
        self.assertEqual(parsed["key"], "value")

    def test_export_pretty(self):
        data = {"key": "value"}
        output = self.processor.export(data, "pretty")
        self.assertIn("\n", output)

    def test_export_invalid_format_raises(self):
        with self.assertRaises(ValueError):
            self.processor.export({}, "xml")


# ──────────────────────────────────────────────────────────────────────────────
# CSVProcessor tests (10 tests)
# ──────────────────────────────────────────────────────────────────────────────

class TestCSVProcessor(unittest.TestCase):

    def setUp(self):
        self.processor = CSVProcessor()
        self.csv_data = "name,age,score\nAlice,30,95.5\nBob,25,88.0\nCarol,35,72.3"

    def test_parse_basic_csv(self):
        result = self.processor.run(self.csv_data, ProcessConfig())
        self.assertTrue(result.success)
        self.assertIsInstance(result.data, list)
        self.assertEqual(len(result.data), 3)

    def test_parse_type_detection_int(self):
        result = self.processor.run(self.csv_data, ProcessConfig())
        self.assertTrue(result.success)
        alice = result.data[0]
        self.assertIsInstance(alice["age"], int)

    def test_parse_type_detection_float(self):
        result = self.processor.run(self.csv_data, ProcessConfig())
        self.assertTrue(result.success)
        alice = result.data[0]
        self.assertIsInstance(alice["score"], float)

    def test_filter_equal(self):
        config = ProcessConfig(filters=["name=Alice"])
        result = self.processor.run(self.csv_data, config)
        self.assertTrue(result.success)
        self.assertEqual(len(result.data), 1)
        self.assertEqual(result.data[0]["name"], "Alice")

    def test_filter_greater_than(self):
        config = ProcessConfig(filters=["age>27"])
        result = self.processor.run(self.csv_data, config)
        self.assertTrue(result.success)
        # Alice(30) and Carol(35)
        self.assertEqual(len(result.data), 2)

    def test_sort_ascending(self):
        config = ProcessConfig(sort_by="age", sort_ascending=True)
        result = self.processor.run(self.csv_data, config)
        self.assertTrue(result.success)
        ages = [r["age"] for r in result.data]
        self.assertEqual(ages, sorted(ages))

    def test_sort_descending(self):
        config = ProcessConfig(sort_by="age", sort_ascending=False)
        result = self.processor.run(self.csv_data, config)
        self.assertTrue(result.success)
        ages = [r["age"] for r in result.data]
        self.assertEqual(ages, sorted(ages, reverse=True))

    def test_export_csv(self):
        data = [{"name": "Alice", "age": 30}]
        output = self.processor.export(data, "csv")
        self.assertIn("name", output)
        self.assertIn("Alice", output)

    def test_export_json(self):
        data = [{"name": "Alice", "age": 30}]
        output = self.processor.export(data, "json")
        parsed = json.loads(output)
        self.assertEqual(parsed[0]["name"], "Alice")

    def test_get_column_types(self):
        data = [{"name": "Alice", "age": 30, "score": 95.5}]
        col_types = self.processor.get_column_types(data)
        self.assertEqual(col_types["age"], "int")
        self.assertEqual(col_types["score"], "float")
        self.assertEqual(col_types["name"], "string")


# ──────────────────────────────────────────────────────────────────────────────
# TextProcessor tests (10 tests)
# ──────────────────────────────────────────────────────────────────────────────

class TestTextProcessor(unittest.TestCase):

    def setUp(self):
        self.processor = TextProcessor()
        self.text = "Hello world\nFoo bar baz\nHello again\nThe quick brown fox"

    def test_parse_returns_lines(self):
        result = self.processor.run(self.text, ProcessConfig())
        self.assertTrue(result.success)
        self.assertEqual(len(result.data), 4)

    def test_filter_lines_contains(self):
        config = ProcessConfig(filters=["Hello"])
        result = self.processor.run(self.text, config)
        self.assertTrue(result.success)
        self.assertEqual(len(result.data), 2)

    def test_filter_lines_case_insensitive(self):
        lines = self.processor.parse(self.text)
        filtered = self.processor.filter_lines(lines, "hello", case_sensitive=False)
        self.assertEqual(len(filtered), 2)

    def test_filter_lines_case_sensitive(self):
        lines = self.processor.parse(self.text)
        filtered = self.processor.filter_lines(lines, "hello", case_sensitive=True)
        self.assertEqual(len(filtered), 0)

    def test_get_stats_counts(self):
        lines = self.processor.parse(self.text)
        stats = self.processor.get_stats(lines)
        self.assertEqual(stats["line_count"], 4)
        self.assertGreater(stats["word_count"], 0)
        self.assertGreater(stats["char_count"], 0)

    def test_find_pattern(self):
        lines = self.processor.parse(self.text)
        matches = self.processor.find_pattern(lines, r"Hello")
        self.assertEqual(len(matches), 2)
        self.assertIn("line_number", matches[0])
        self.assertIn("match", matches[0])

    def test_replace_pattern(self):
        lines = self.processor.parse(self.text)
        replaced = self.processor.replace_pattern(lines, r"Hello", "Hi")
        self.assertTrue(replaced[0].startswith("Hi"))

    def test_export_text(self):
        data = ["line one", "line two"]
        output = self.processor.export(data, "text")
        self.assertIn("line one", output)
        self.assertIn("line two", output)

    def test_export_json(self):
        data = ["line one", "line two"]
        output = self.processor.export(data, "json")
        parsed = json.loads(output)
        self.assertEqual(parsed[0], "line one")

    def test_empty_input(self):
        result = self.processor.run("", ProcessConfig())
        self.assertTrue(result.success)
        self.assertEqual(result.data, [])


# ──────────────────────────────────────────────────────────────────────────────
# PluginMetadataRecord tests (5 tests)
# ──────────────────────────────────────────────────────────────────────────────

class TestPluginMetadataRecord(unittest.TestCase):

    def test_defaults(self):
        p = PluginMetadataRecord(name="test_plugin")
        self.assertEqual(p.name, "test_plugin")
        self.assertEqual(p.version, "1.0.0")
        self.assertTrue(p.enabled)
        self.assertEqual(p.capabilities, [])

    def test_to_dict(self):
        p = PluginMetadataRecord(name="p", description="desc")
        d = p.to_dict()
        self.assertEqual(d["name"], "p")
        self.assertEqual(d["description"], "desc")

    def test_from_dict(self):
        d = {"name": "p", "version": "2.0.0", "capabilities": ["x"]}
        p = PluginMetadataRecord.from_dict(d)
        self.assertEqual(p.name, "p")
        self.assertEqual(p.version, "2.0.0")
        self.assertEqual(p.capabilities, ["x"])

    def test_from_dict_ignores_unknown_keys(self):
        d = {"name": "p", "unknown_field": "value"}
        p = PluginMetadataRecord.from_dict(d)
        self.assertEqual(p.name, "p")

    def test_has_timestamps(self):
        p = PluginMetadataRecord(name="p")
        self.assertIsNotNone(p.created_at)
        self.assertIsNotNone(p.updated_at)


# ──────────────────────────────────────────────────────────────────────────────
# PluginRegistryManager tests (15 tests)
# ──────────────────────────────────────────────────────────────────────────────

class TestPluginRegistryManager(unittest.TestCase):

    def _make_plugin(self, name, category="general", capabilities=None, tags=None, deps=None):
        return PluginMetadataRecord(
            name=name,
            description=f"Plugin {name}",
            category=category,
            capabilities=capabilities or [],
            tags=tags or [],
            dependencies=deps or [],
        )

    def test_register_and_get(self):
        registry = PluginRegistryManager()
        p = self._make_plugin("alpha")
        registry.register(p)
        retrieved = registry.get("alpha")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, "alpha")

    def test_register_updates_existing(self):
        registry = PluginRegistryManager()
        registry.register(self._make_plugin("alpha"))
        updated = self._make_plugin("alpha")
        updated.description = "Updated"
        registry.register(updated)
        self.assertEqual(registry.get("alpha").description, "Updated")

    def test_unregister(self):
        registry = PluginRegistryManager()
        registry.register(self._make_plugin("alpha"))
        result = registry.unregister("alpha")
        self.assertTrue(result)
        self.assertIsNone(registry.get("alpha"))

    def test_unregister_nonexistent_returns_false(self):
        registry = PluginRegistryManager()
        result = registry.unregister("nonexistent")
        self.assertFalse(result)

    def test_list_all(self):
        registry = PluginRegistryManager()
        registry.register(self._make_plugin("a"))
        registry.register(self._make_plugin("b"))
        all_plugins = registry.list_all()
        self.assertEqual(len(all_plugins), 2)

    def test_find_by_capability(self):
        registry = PluginRegistryManager()
        registry.register(self._make_plugin("proc", capabilities=["data-processing"]))
        registry.register(self._make_plugin("other"))
        results = registry.find_by_capability("data-processing")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "proc")

    def test_find_by_capability_partial_match(self):
        registry = PluginRegistryManager()
        registry.register(self._make_plugin("proc", capabilities=["data-processing-v2"]))
        results = registry.find_by_capability("data")
        self.assertEqual(len(results), 1)

    def test_find_by_tag(self):
        registry = PluginRegistryManager()
        registry.register(self._make_plugin("tagged", tags=["ml", "ai"]))
        registry.register(self._make_plugin("other", tags=["sql"]))
        results = registry.find_by_tag("ml")
        self.assertEqual(len(results), 1)

    def test_find_by_category(self):
        registry = PluginRegistryManager()
        registry.register(self._make_plugin("a", category="analytics"))
        registry.register(self._make_plugin("b", category="io"))
        results = registry.find_by_category("analytics")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "a")

    def test_search_by_name(self):
        registry = PluginRegistryManager()
        registry.register(self._make_plugin("my_special_plugin"))
        registry.register(self._make_plugin("other"))
        result = registry.search("special")
        self.assertIsInstance(result, RegistrySearchResult)
        self.assertEqual(len(result.plugins), 1)

    def test_search_no_results(self):
        registry = PluginRegistryManager()
        registry.register(self._make_plugin("alpha"))
        result = registry.search("zzz")
        self.assertEqual(result.total_found, 0)

    def test_resolve_dependencies_simple(self):
        registry = PluginRegistryManager()
        registry.register(self._make_plugin("base"))
        registry.register(self._make_plugin("child", deps=["base"]))
        deps = registry.resolve_dependencies("child")
        self.assertIn("base", deps)

    def test_resolve_dependencies_circular_raises(self):
        registry = PluginRegistryManager()
        registry.register(self._make_plugin("a", deps=["b"]))
        registry.register(self._make_plugin("b", deps=["a"]))
        with self.assertRaises(ValueError) as ctx:
            registry.resolve_dependencies("a")
        self.assertIn("Circular", str(ctx.exception))

    def test_export_and_import_json(self):
        registry = PluginRegistryManager()
        registry.register(self._make_plugin("alpha", capabilities=["x"]))
        json_str = registry.export_json()
        parsed = json.loads(json_str)
        self.assertIn("plugins", parsed)

        new_registry = PluginRegistryManager()
        count = new_registry.import_json(json_str)
        self.assertEqual(count, 1)
        self.assertIsNotNone(new_registry.get("alpha"))

    def test_persist_to_file(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            registry = PluginRegistryManager(registry_path=path)
            registry.register(self._make_plugin("saved"))
            # Load from file
            registry2 = PluginRegistryManager(registry_path=path)
            self.assertIsNotNone(registry2.get("saved"))
        finally:
            if os.path.exists(path):
                os.unlink(path)


# ──────────────────────────────────────────────────────────────────────────────
# PluginWizardBackend tests (15 tests)
# ──────────────────────────────────────────────────────────────────────────────

class TestPluginWizardBackend(unittest.TestCase):

    def _valid_wizard(self):
        wizard = PluginWizardBackend()
        wizard.set_basic_info("my_plugin", "A test plugin", "Alice")
        wizard.set_type("processor")
        return wizard

    def test_set_basic_info(self):
        wizard = PluginWizardBackend()
        wizard.set_basic_info("test_plugin", "desc", "Author")
        state = wizard.get_state()
        self.assertEqual(state["name"], "test_plugin")
        self.assertEqual(state["author"], "Author")

    def test_set_type_valid(self):
        wizard = PluginWizardBackend()
        wizard.set_type("analyzer")
        self.assertEqual(wizard.get_state()["plugin_type"], "analyzer")

    def test_set_type_invalid_raises(self):
        wizard = PluginWizardBackend()
        with self.assertRaises(ValueError):
            wizard.set_type("unknown_type")

    def test_set_capabilities(self):
        wizard = self._valid_wizard()
        wizard.set_capabilities(["x", "y"])
        self.assertEqual(wizard.get_state()["capabilities"], ["x", "y"])

    def test_set_dependencies(self):
        wizard = self._valid_wizard()
        wizard.set_dependencies(["base_plugin"])
        self.assertEqual(wizard.get_state()["dependencies"], ["base_plugin"])

    def test_set_tags_and_hooks(self):
        wizard = self._valid_wizard()
        wizard.set_tags(["ai"]).set_hooks(["on_load"])
        state = wizard.get_state()
        self.assertIn("ai", state["tags"])
        self.assertIn("on_load", state["hooks"])

    def test_validate_passes(self):
        wizard = self._valid_wizard()
        errors = wizard.validate()
        self.assertEqual(errors, [])

    def test_validate_missing_name(self):
        wizard = PluginWizardBackend()
        wizard.set_basic_info("", "desc", "author")
        errors = wizard.validate()
        self.assertTrue(any(e.step == "basic_info" for e in errors))

    def test_validate_missing_description(self):
        wizard = PluginWizardBackend()
        wizard.set_basic_info("my_plugin", "")
        errors = wizard.validate()
        self.assertTrue(any("description" in e.message.lower() for e in errors))

    def test_finalize_produces_result(self):
        wizard = self._valid_wizard()
        result = wizard.finalize()
        self.assertIsInstance(result, WizardResult)
        self.assertIn("my_plugin", result.plugin_code)
        self.assertIn("my_plugin", result.plugin_name)

    def test_finalize_produces_manifest(self):
        wizard = self._valid_wizard()
        wizard.set_capabilities(["proc"])
        result = wizard.finalize()
        manifest = result.manifest_dict
        self.assertEqual(manifest["name"], "my_plugin")
        self.assertIn("proc", manifest["capabilities"])

    def test_finalize_invalid_raises(self):
        wizard = PluginWizardBackend()
        with self.assertRaises(WizardValidationError):
            wizard.finalize()

    def test_generate_code_class_name(self):
        wizard = PluginWizardBackend()
        wizard.set_basic_info("my_plugin", "desc")
        code = wizard.generate_plugin_code()
        self.assertIn("class MyPlugin", code)

    def test_generate_processor_code_contains_method(self):
        wizard = PluginWizardBackend()
        wizard.set_basic_info("my_plugin", "desc")
        wizard.set_type("processor")
        code = wizard.generate_plugin_code()
        self.assertIn("def process(", code)

    def test_reset(self):
        wizard = self._valid_wizard()
        wizard.reset()
        state = wizard.get_state()
        self.assertEqual(state["name"], "")

    def test_to_class_name_helper(self):
        self.assertEqual(_to_class_name("my_plugin"), "MyPlugin")
        self.assertEqual(_to_class_name("data_processor_v2"), "DataProcessorV2")
        self.assertEqual(_to_class_name("simple"), "Simple")


# ──────────────────────────────────────────────────────────────────────────────
# Runner
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    test_classes = [
        TestJSONProcessor,
        TestCSVProcessor,
        TestTextProcessor,
        TestPluginMetadataRecord,
        TestPluginRegistryManager,
        TestPluginWizardBackend,
    ]

    for cls in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(cls))

    total = suite.countTestCases()
    print(f"Running {total} tests for Task 3 Plugin System...")
    print("=" * 60)

    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)

    print("=" * 60)
    passed = total - len(result.failures) - len(result.errors)
    print(f"\nResult: {passed}/{total} tests passed")

    if result.failures:
        print(f"\nFAILURES ({len(result.failures)}):")
        for test, trace in result.failures:
            print(f"  FAIL: {test}")
            for line in trace.strip().split("\n")[-3:]:
                print(f"    {line}")

    if result.errors:
        print(f"\nERRORS ({len(result.errors)}):")
        for test, trace in result.errors:
            print(f"  ERROR: {test}")
            for line in trace.strip().split("\n")[-3:]:
                print(f"    {line}")

    sys.exit(0 if result.wasSuccessful() else 1)
