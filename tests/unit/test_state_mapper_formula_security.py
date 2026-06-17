"""Security tests for Lyrixa state-mapping formulas."""

from Aetherra.lyrixa.interactive.state_mapper import StateMapper


def test_intensity_formula_supports_bounded_arithmetic():
    mapper = StateMapper.__new__(StateMapper)

    assert mapper._evaluate_intensity_formula("min(1, score * 2)", {"score": 0.4}) == 0.8
    assert mapper._evaluate_intensity_formula("score * 3", {"score": 0.6}) == 1.0


def test_intensity_formula_rejects_code_execution(tmp_path):
    mapper = StateMapper.__new__(StateMapper)
    marker = tmp_path / "formula-side-effect.txt"
    formula = f"__import__('pathlib').Path({str(marker)!r}).write_text('bad')"

    assert mapper._evaluate_intensity_formula(formula, {}) == 0.5
    assert not marker.exists()
