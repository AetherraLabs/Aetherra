"""Verify discovery exclusions and negations without modifying runtime policy."""

import os

from Aetherra.aetherra_core.system.ignore_pattern_loader import (
    IgnorePattern,
    IgnorePatternLoader,
)


def test_create_pattern():
    pattern = IgnorePattern(pattern="*.pyc", is_negation=False, is_directory=False)
    assert pattern.pattern == "*.pyc"
    assert not pattern.is_negation


def test_pattern_glob_matching():
    pattern = IgnorePattern(pattern="*.py", is_regex=False)
    assert pattern.matches("test.py")
    assert not pattern.matches("test.txt")


def test_pattern_directory_matching():
    pattern = IgnorePattern(pattern="build/", is_directory=True)
    assert pattern.matches("build/")
    assert pattern.matches("build/output")


def test_pattern_negation():
    pattern = IgnorePattern(pattern="!important.txt", is_negation=True)
    assert pattern.is_negation
    assert pattern.pattern == "!important.txt"


def test_create_loader(tmp_path):
    loader = IgnorePatternLoader(str(tmp_path))
    assert loader is not None
    assert loader.root_dir == tmp_path


def test_load_default_patterns(tmp_path):
    loader = IgnorePatternLoader(str(tmp_path), use_defaults=True)
    success, patterns = loader.load()
    assert success
    assert len(patterns) > 0


def test_load_from_ignore_file(tmp_path):
    (tmp_path / ".aetherraignore").write_text(
        "# Comment\nbuild/\ndist/\n*.pyc\n", encoding="utf-8"
    )
    loader = IgnorePatternLoader(str(tmp_path), use_defaults=False)
    success, patterns = loader.load()
    assert success
    assert "build/" in patterns
    assert "dist/" in patterns
    assert "*.pyc" in patterns


def test_ignore_file_comments(tmp_path):
    (tmp_path / ".aetherraignore").write_text(
        "# This is a comment\n*.pyc\n\n  # Indented comment\nbuild/\n", encoding="utf-8"
    )
    loader = IgnorePatternLoader(str(tmp_path), use_defaults=False)
    success, patterns = loader.load()
    assert success
    assert patterns == {"*.pyc", "build/"}


def test_negation_patterns(tmp_path):
    (tmp_path / ".aetherraignore").write_text(
        "*.log\n!important.log\n", encoding="utf-8"
    )
    loader = IgnorePatternLoader(str(tmp_path), use_defaults=False)
    success, _ = loader.load()
    assert success
    assert loader.should_ignore("test.log")
    assert not loader.should_ignore("important.log")


def test_should_ignore_simple(tmp_path):
    loader = IgnorePatternLoader(str(tmp_path), use_defaults=False)
    loader.patterns = [
        IgnorePattern(pattern="*.pyc"),
        IgnorePattern(pattern="__pycache__/"),
    ]
    assert loader.should_ignore("test.pyc")
    assert not loader.should_ignore("test.py")
    assert loader.should_ignore("__pycache__/modules")


def test_should_ignore_directory(tmp_path):
    loader = IgnorePatternLoader(str(tmp_path), use_defaults=False)
    loader.patterns = [
        IgnorePattern(pattern="build/", is_directory=True),
        IgnorePattern(pattern="dist/", is_directory=True),
    ]
    assert loader.should_ignore_directory("build")
    assert loader.should_ignore_directory("dist")
    assert not loader.should_ignore_directory("src")


def test_normalize_pattern(tmp_path):
    loader = IgnorePatternLoader(str(tmp_path), use_defaults=False)
    normalized = loader._normalize_pattern("src\\main\\*.py")
    assert "/" in normalized
    assert "\\" not in normalized
    assert not loader._normalize_pattern("/build/").startswith("/")


def test_find_ignore_file(tmp_path):
    ignore_file = tmp_path / ".aetherraignore"
    ignore_file.write_text("*.pyc\n", encoding="utf-8")
    loader = IgnorePatternLoader(str(tmp_path))
    assert loader._find_ignore_file() == ignore_file


def test_list_patterns(tmp_path):
    (tmp_path / ".aetherraignore").write_text("*.pyc\nbuild/\n", encoding="utf-8")
    loader = IgnorePatternLoader(str(tmp_path), use_defaults=False)
    loader.load()
    patterns = loader.list_patterns(include_negations=False)
    assert len(patterns) > 0
    assert "*.pyc" in patterns
    assert "build/" in patterns


def test_get_pattern_info(tmp_path):
    (tmp_path / ".aetherraignore").write_text(
        "*.pyc\nbuild/\n!important.pyc\n", encoding="utf-8"
    )
    loader = IgnorePatternLoader(str(tmp_path), use_defaults=False)
    loader.load()
    info = loader.get_pattern_info()
    assert "total_patterns" in info
    assert "ignore_patterns" in info
    assert "negation_patterns" in info
    assert info["total_patterns"] > 0


def test_glob_patterns_subdirs(tmp_path):
    loader = IgnorePatternLoader(str(tmp_path), use_defaults=False)
    loader.patterns = [IgnorePattern(pattern="tests/**/test_*.py")]
    tests_dir = tmp_path / "tests" / "unit"
    tests_dir.mkdir(parents=True)
    test_file = tests_dir / "test_foo.py"
    test_file.touch()
    assert loader.should_ignore(test_file.relative_to(tmp_path).as_posix())
    assert not loader.should_ignore("tests/unit/helper.py")


def test_empty_ignore_file(tmp_path):
    (tmp_path / ".aetherraignore").write_text("", encoding="utf-8")
    loader = IgnorePatternLoader(str(tmp_path), use_defaults=True)
    success, patterns = loader.load()
    assert success
    assert len(patterns) > 0


def test_get_ignored_paths(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "build").mkdir()
    (tmp_path / "src" / "main.py").touch()
    (tmp_path / "build" / "output.o").touch()
    loader = IgnorePatternLoader(str(tmp_path), use_defaults=False)
    loader.patterns = [IgnorePattern(pattern="build/", is_directory=True)]
    ignored = loader.get_ignored_paths()
    assert "build" in ignored
    assert "build/output.o" in ignored
    assert "src/main.py" not in ignored


def test_multiple_wildcards():
    pattern = IgnorePattern(pattern="*.*.pyc")
    assert pattern.matches("test.backup.pyc")
    assert not pattern.matches("test.pyc")
    assert not pattern.matches("test.py")


def test_pattern_priority_negation(tmp_path):
    loader = IgnorePatternLoader(str(tmp_path), use_defaults=False)
    loader.patterns = [
        IgnorePattern(pattern="*.log"),
        IgnorePattern(pattern="!error.log", is_negation=True),
    ]
    loader._process_patterns()
    assert not loader.should_ignore("error.log")
    assert loader.should_ignore("other.log")


def test_case_sensitivity():
    pattern = IgnorePattern(pattern="*.PYC")
    # fnmatch normalizes case according to the host OS.
    assert pattern.matches("test.pyc") == (os.path.normcase("PYC") == "pyc")
    assert pattern.matches("test.PYC")


def test_special_characters_in_patterns():
    pattern1 = IgnorePattern(pattern="temp*")
    pattern2 = IgnorePattern(pattern="[a-z]*.txt")
    assert pattern1.matches("temporary")
    assert pattern1.matches("temp")
    assert pattern2.matches("abc.txt")
    assert not pattern2.matches("123.txt")


def test_directory_vs_file_patterns():
    dir_pattern = IgnorePattern(pattern="logs/", is_directory=True)
    file_pattern = IgnorePattern(pattern="*.log")
    assert dir_pattern.matches("logs/")
    assert file_pattern.matches("app.log")
