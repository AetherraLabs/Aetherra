"""
Standalone test runner for Task 3: Plugin System
Tests: plugin_processors.py, plugin_metadata_registry.py, plugin_wizard_backend.py

Run with:
    python -m tests.legacy.root_standalone.test_plugin_system_standalone
"""

# Standard library imports
import json
import os
import sys
import tempfile
import unittest

# Third party imports
import pytest

# Aetherra imports
from Aetherra.plugins.core.plugin_metadata_registry import (
    PluginMetadataRecord,
    PluginRegistryManager,
    RegistrySearchResult,
)
from Aetherra.plugins.core.plugin_processors import (
    CSVProcessor,
    JSONProcessor,
    ProcessConfig,
    TextProcessor,
)
from Aetherra.plugins.core.plugin_wizard_backend import (
    PluginWizardBackend,
    WizardResult,
    WizardValidationError,
    _to_class_name,
)

# JSONProcessor tests (10 tests)


class TestJSONProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = JSONProcessor()

    def test_parse_valid_dict(self):
        data = self.processor.parse('{"key": "value", "num": 42}')
        assert data["key"] == "value"
        assert data["num"] == 42

    def test_parse_valid_list(self):
        data = self.processor.parse('[{"id": 1}, {"id": 2}]')
        assert isinstance(data, list)
        assert len(data) == 2

    def test_parse_invalid_json_returns_error(self):
        result = self.processor.run("not json", ProcessConfig())
        assert not result.success
        assert "json" in result.error.lower()

    def test_schema_validation_pass(self):
        data = [{"name": "Alice", "age": 30}]
        schema = {"required": ["name", "age"]}
        errors = self.processor.validate_schema(data, schema)
        assert errors == []

    def test_schema_validation_fail_missing_field(self):
        data = [{"name": "Alice"}]
        schema = {"required": ["name", "age"]}
        errors = self.processor.validate_schema(data, schema)
        assert len(errors) > 0

    def test_filter_by_callable(self):
        data = [{"age": 25}, {"age": 40}, {"age": 18}]
        filtered = self.processor.filter(data, lambda r: r["age"] >= 25)
        assert len(filtered) == 2

    def test_transform(self):
        data = [{"x": 1}, {"x": 2}]
        result = self.processor.transform(data, lambda item: {"y": item["x"] * 2})
        assert result[0]["y"] == 2

    def test_export_json(self):
        data = {"key": "value"}
        output = self.processor.export(data, "json")
        parsed = json.loads(output)
        assert parsed["key"] == "value"

    def test_export_pretty(self):
        data = {"key": "value"}
        output = self.processor.export(data, "pretty")
        assert "\n" in output

    def test_export_invalid_format_raises(self):
        with pytest.raises(ValueError, match="Unsupported format: xml"):
            self.processor.export({}, "xml")


# CSVProcessor tests (10 tests)


class TestCSVProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = CSVProcessor()
        self.csv_data = "name,age,score\nAlice,30,95.5\nBob,25,88.0\nCarol,35,72.3"

    def test_parse_basic_csv(self):
        result = self.processor.run(self.csv_data, ProcessConfig())
        assert result.success
        assert isinstance(result.data, list)
        assert len(result.data) == 3

    def test_parse_type_detection_int(self):
        result = self.processor.run(self.csv_data, ProcessConfig())
        assert result.success
        alice = result.data[0]
        assert isinstance(alice["age"], int)

    def test_parse_type_detection_float(self):
        result = self.processor.run(self.csv_data, ProcessConfig())
        assert result.success
        alice = result.data[0]
        assert isinstance(alice["score"], float)

    def test_filter_equal(self):
        config = ProcessConfig(filters=["name=Alice"])
        result = self.processor.run(self.csv_data, config)
        assert result.success
        assert len(result.data) == 1
        assert result.data[0]["name"] == "Alice"

    def test_filter_greater_than(self):
        config = ProcessConfig(filters=["age>27"])
        result = self.processor.run(self.csv_data, config)
        assert result.success
        # Alice(30) and Carol(35)
        assert len(result.data) == 2

    def test_sort_ascending(self):
        config = ProcessConfig(sort_by="age", sort_ascending=True)
        result = self.processor.run(self.csv_data, config)
        assert result.success
        ages = [r["age"] for r in result.data]
        assert ages == sorted(ages)

    def test_sort_descending(self):
        config = ProcessConfig(sort_by="age", sort_ascending=False)
        result = self.processor.run(self.csv_data, config)
        assert result.success
        ages = [r["age"] for r in result.data]
        assert ages == sorted(ages, reverse=True)

    def test_export_csv(self):
        data = [{"name": "Alice", "age": 30}]
        output = self.processor.export(data, "csv")
        assert "name" in output
        assert "Alice" in output

    def test_export_json(self):
        data = [{"name": "Alice", "age": 30}]
        output = self.processor.export(data, "json")
        parsed = json.loads(output)
        assert parsed[0]["name"] == "Alice"

    def test_get_column_types(self):
        data = [{"name": "Alice", "age": 30, "score": 95.5}]
        col_types = self.processor.get_column_types(data)
        assert col_types["age"] == "int"
        assert col_types["score"] == "float"
        assert col_types["name"] == "string"


# TextProcessor tests (10 tests)


class TestTextProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = TextProcessor()
        self.text = "Hello world\nFoo bar baz\nHello again\nThe quick brown fox"

    def test_parse_returns_lines(self):
        result = self.processor.run(self.text, ProcessConfig())
        assert result.success
        assert len(result.data) == 4

    def test_filter_lines_contains(self):
        config = ProcessConfig(filters=["Hello"])
        result = self.processor.run(self.text, config)
        assert result.success
        assert len(result.data) == 2

    def test_filter_lines_case_insensitive(self):
        lines = self.processor.parse(self.text)
        filtered = self.processor.filter_lines(lines, "hello", case_sensitive=False)
        assert len(filtered) == 2

    def test_filter_lines_case_sensitive(self):
        lines = self.processor.parse(self.text)
        filtered = self.processor.filter_lines(lines, "hello", case_sensitive=True)
        assert len(filtered) == 0

    def test_get_stats_counts(self):
        lines = self.processor.parse(self.text)
        stats = self.processor.get_stats(lines)
        assert stats["line_count"] == 4
        assert stats["word_count"] > 0
        assert stats["char_count"] > 0

    def test_find_pattern(self):
        lines = self.processor.parse(self.text)
        matches = self.processor.find_pattern(lines, r"Hello")
        assert len(matches) == 2
        assert "line_number" in matches[0]
        assert "match" in matches[0]

    def test_replace_pattern(self):
        lines = self.processor.parse(self.text)
        replaced = self.processor.replace_pattern(lines, r"Hello", "Hi")
        assert replaced[0].startswith("Hi")

    def test_export_text(self):
        data = ["line one", "line two"]
        output = self.processor.export(data, "text")
        assert "line one" in output
        assert "line two" in output

    def test_export_json(self):
        data = ["line one", "line two"]
        output = self.processor.export(data, "json")
        parsed = json.loads(output)
        assert parsed[0] == "line one"

    def test_empty_input(self):
        result = self.processor.run("", ProcessConfig())
        assert result.success
        assert result.data == []


# PluginMetadataRecord tests (5 tests)


class TestPluginMetadataRecord(unittest.TestCase):
    def test_defaults(self):
        p = PluginMetadataRecord(name="test_plugin")
        assert p.name == "test_plugin"
        assert p.version == "1.0.0"
        assert p.enabled
        assert p.capabilities == []

    def test_to_dict(self):
        p = PluginMetadataRecord(name="p", description="desc")
        d = p.to_dict()
        assert d["name"] == "p"
        assert d["description"] == "desc"

    def test_from_dict(self):
        d = {"name": "p", "version": "2.0.0", "capabilities": ["x"]}
        p = PluginMetadataRecord.from_dict(d)
        assert p.name == "p"
        assert p.version == "2.0.0"
        assert p.capabilities == ["x"]

    def test_from_dict_ignores_unknown_keys(self):
        d = {"name": "p", "unknown_field": "value"}
        p = PluginMetadataRecord.from_dict(d)
        assert p.name == "p"

    def test_has_timestamps(self):
        p = PluginMetadataRecord(name="p")
        assert p.created_at is not None
        assert p.updated_at is not None


# PluginRegistryManager tests (15 tests)


class TestPluginRegistryManager(unittest.TestCase):
    def _make_plugin(
        self, name, category="general", capabilities=None, tags=None, deps=None
    ):
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
        assert retrieved is not None
        assert retrieved.name == "alpha"

    def test_register_updates_existing(self):
        registry = PluginRegistryManager()
        registry.register(self._make_plugin("alpha"))
        updated = self._make_plugin("alpha")
        updated.description = "Updated"
        registry.register(updated)
        assert registry.get("alpha").description == "Updated"

    def test_unregister(self):
        registry = PluginRegistryManager()
        registry.register(self._make_plugin("alpha"))
        result = registry.unregister("alpha")
        assert result
        assert registry.get("alpha") is None

    def test_unregister_nonexistent_returns_false(self):
        registry = PluginRegistryManager()
        result = registry.unregister("nonexistent")
        assert not result

    def test_list_all(self):
        registry = PluginRegistryManager()
        registry.register(self._make_plugin("a"))
        registry.register(self._make_plugin("b"))
        all_plugins = registry.list_all()
        assert len(all_plugins) == 2

    def test_find_by_capability(self):
        registry = PluginRegistryManager()
        registry.register(self._make_plugin("proc", capabilities=["data-processing"]))
        registry.register(self._make_plugin("other"))
        results = registry.find_by_capability("data-processing")
        assert len(results) == 1
        assert results[0].name == "proc"

    def test_find_by_capability_partial_match(self):
        registry = PluginRegistryManager()
        registry.register(
            self._make_plugin("proc", capabilities=["data-processing-v2"])
        )
        results = registry.find_by_capability("data")
        assert len(results) == 1

    def test_find_by_tag(self):
        registry = PluginRegistryManager()
        registry.register(self._make_plugin("tagged", tags=["ml", "ai"]))
        registry.register(self._make_plugin("other", tags=["sql"]))
        results = registry.find_by_tag("ml")
        assert len(results) == 1

    def test_find_by_category(self):
        registry = PluginRegistryManager()
        registry.register(self._make_plugin("a", category="analytics"))
        registry.register(self._make_plugin("b", category="io"))
        results = registry.find_by_category("analytics")
        assert len(results) == 1
        assert results[0].name == "a"

    def test_search_by_name(self):
        registry = PluginRegistryManager()
        registry.register(self._make_plugin("my_special_plugin"))
        registry.register(self._make_plugin("other"))
        result = registry.search("special")
        assert isinstance(result, RegistrySearchResult)
        assert len(result.plugins) == 1

    def test_search_no_results(self):
        registry = PluginRegistryManager()
        registry.register(self._make_plugin("alpha"))
        result = registry.search("zzz")
        assert result.total_found == 0

    def test_resolve_dependencies_simple(self):
        registry = PluginRegistryManager()
        registry.register(self._make_plugin("base"))
        registry.register(self._make_plugin("child", deps=["base"]))
        deps = registry.resolve_dependencies("child")
        assert "base" in deps

    def test_resolve_dependencies_circular_raises(self):
        registry = PluginRegistryManager()
        registry.register(self._make_plugin("a", deps=["b"]))
        registry.register(self._make_plugin("b", deps=["a"]))
        with pytest.raises(ValueError, match="Circular") as ctx:
            registry.resolve_dependencies("a")
        assert "Circular" in str(ctx.value)

    def test_export_and_import_json(self):
        registry = PluginRegistryManager()
        registry.register(self._make_plugin("alpha", capabilities=["x"]))
        json_str = registry.export_json()
        parsed = json.loads(json_str)
        assert "plugins" in parsed

        new_registry = PluginRegistryManager()
        count = new_registry.import_json(json_str)
        assert count == 1
        assert new_registry.get("alpha") is not None

    def test_persist_to_file(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            registry = PluginRegistryManager(registry_path=path)
            registry.register(self._make_plugin("saved"))
            # Load from file
            registry2 = PluginRegistryManager(registry_path=path)
            assert registry2.get("saved") is not None
        finally:
            if os.path.exists(path):
                os.unlink(path)


# PluginWizardBackend tests (15 tests)


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
        assert state["name"] == "test_plugin"
        assert state["author"] == "Author"

    def test_set_type_valid(self):
        wizard = PluginWizardBackend()
        wizard.set_type("analyzer")
        assert wizard.get_state()["plugin_type"] == "analyzer"

    def test_set_type_invalid_raises(self):
        wizard = PluginWizardBackend()
        with pytest.raises(ValueError, match="Unsupported type 'unknown_type'"):
            wizard.set_type("unknown_type")

    def test_set_capabilities(self):
        wizard = self._valid_wizard()
        wizard.set_capabilities(["x", "y"])
        assert wizard.get_state()["capabilities"] == ["x", "y"]

    def test_set_dependencies(self):
        wizard = self._valid_wizard()
        wizard.set_dependencies(["base_plugin"])
        assert wizard.get_state()["dependencies"] == ["base_plugin"]

    def test_set_tags_and_hooks(self):
        wizard = self._valid_wizard()
        wizard.set_tags(["ai"]).set_hooks(["on_load"])
        state = wizard.get_state()
        assert "ai" in state["tags"]
        assert "on_load" in state["hooks"]

    def test_validate_passes(self):
        wizard = self._valid_wizard()
        errors = wizard.validate()
        assert errors == []

    def test_validate_missing_name(self):
        wizard = PluginWizardBackend()
        wizard.set_basic_info("", "desc", "author")
        errors = wizard.validate()
        assert any(e.step == "basic_info" for e in errors)

    def test_validate_missing_description(self):
        wizard = PluginWizardBackend()
        wizard.set_basic_info("my_plugin", "")
        errors = wizard.validate()
        assert any("description" in e.message.lower() for e in errors)

    def test_finalize_produces_result(self):
        wizard = self._valid_wizard()
        result = wizard.finalize()
        assert isinstance(result, WizardResult)
        assert "my_plugin" in result.plugin_code
        assert "my_plugin" in result.plugin_name

    def test_finalize_produces_manifest(self):
        wizard = self._valid_wizard()
        wizard.set_capabilities(["proc"])
        result = wizard.finalize()
        manifest = result.manifest_dict
        assert manifest["name"] == "my_plugin"
        assert "proc" in manifest["capabilities"]

    def test_finalize_invalid_raises(self):
        wizard = PluginWizardBackend()
        with pytest.raises(WizardValidationError):
            wizard.finalize()

    def test_generate_code_class_name(self):
        wizard = PluginWizardBackend()
        wizard.set_basic_info("my_plugin", "desc")
        code = wizard.generate_plugin_code()
        assert "class MyPlugin" in code

    def test_generate_processor_code_contains_method(self):
        wizard = PluginWizardBackend()
        wizard.set_basic_info("my_plugin", "desc")
        wizard.set_type("processor")
        code = wizard.generate_plugin_code()
        assert "def process(" in code

    def test_reset(self):
        wizard = self._valid_wizard()
        wizard.reset()
        state = wizard.get_state()
        assert state["name"] == ""

    def test_to_class_name_helper(self):
        assert _to_class_name("my_plugin") == "MyPlugin"
        assert _to_class_name("data_processor_v2") == "DataProcessorV2"
        assert _to_class_name("simple") == "Simple"


# Runner

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
