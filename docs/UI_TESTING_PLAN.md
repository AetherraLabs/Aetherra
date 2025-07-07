# aetherra UI Testing Infrastructure

## Overview

This document outlines the testing strategy and implementation plan for ensuring consistent and accessible UI across the aetherra/Lyrixaapplication. The testing infrastructure will verify compliance with the UI Style Guide and accessibility standards.

## Testing Strategy

### 1. Manual Visual Inspection

- **Purpose**: Initial verification of UI consistency
- **Process**:
  - Review all UI components against style guide
  - Screenshot comparison with reference designs
  - Dark mode appearance verification
  - Responsiveness testing across window sizes

### 2. Automated UI Testing

#### Component Testing

- **Tools**: PyTest, pytest-qt
- **Test Cases**:
  - Verify component appearance matches specifications
  - Test component layout and spacing
  - Validate color consistency with style guide
  - Check border-radius and other style properties

```python
# Example test case
def test_button_appearance(qtbot):
    """Test that buttons conform to style guide specifications"""
    # Create button
    button = QPushButton("Test Button")

    # Get button styling
    style = button.styleSheet()

    # Check properties against style guide
    assert "border-radius: 4px" in style
    assert "background-color: #2d2d2d" in style
    assert "color: #ffffff" in style
```

#### Layout Testing

- **Approach**: Validate layout metrics match style guide
- **Test Cases**:
  - Verify spacing between elements
  - Check padding consistency
  - Test alignment of UI components
  - Validate responsive behavior

```python
# Example test case
def test_layout_spacing(qtbot):
    """Test that layout spacing conforms to style guide"""
    # Create layout with components
    layout = QVBoxLayout()
    layout.addWidget(QPushButton("Button 1"))
    layout.addWidget(QPushButton("Button 2"))

    # Check spacing
    assert layout.spacing() == 8  # Standard vertical spacing
```

#### Dark Mode Testing

- **Test Cases**:
  - Verify all UI elements use dark theme colors
  - Test contrast ratios meet accessibility standards
  - Ensure consistency across all components
  - Validate text readability

### 3. Accessibility Testing

- **Tools**: Automated accessibility checkers
- **Test Cases**:
  - Color contrast verification (WCAG 2.1 AA compliance)
  - Keyboard navigation testing
  - Screen reader compatibility
  - Focus indicator visibility

### 4. Cross-Platform Testing

- **Environments**:
  - Windows 10/11
  - macOS
  - Linux (Ubuntu)
- **Aspects to Test**:
  - Font rendering
  - Color accuracy
  - Layout consistency
  - Control sizing

## Implementation Plan

### Phase 1: Test Framework Setup

1. Install testing dependencies:
   ```bash
   pip install pytest pytest-qt pytest-cov
   ```

2. Create basic test structure:
   ```
   tests/
   ├── ui/
   │   ├── __init__.py
   │   ├── test_buttons.py
   │   ├── test_chat_area.py
   │   ├── test_dark_mode.py
   │   ├── test_layout.py
   │   └── test_tabs.py
   ├── conftest.py
   └── __init__.py
   ```

3. Implement fixture for standard app initialization:
   ```python
   # conftest.py
   import pytest
   from PySide6.QtWidgets import QApplication

   @pytest.fixture
   def app(qtbot):
       """Create a QApplication instance for testing."""
       app = QApplication.instance() or QApplication([])
       yield app
   ```

### Phase 2: Component Tests

1. Create test cases for core UI components:
   - Buttons
   - Input fields
   - Text displays
   - Tabs
   - Chat messages

2. Verify styling against UI Style Guide:
   - Colors
   - Typography
   - Spacing
   - Border radius

### Phase 3: Integration Tests

1. Test complete UI flows:
   - Chat interaction
   - Tab switching
   - Code preview
   - Settings panel

2. Verify component interactions maintain styling

### Phase 4: Automated UI Screenshots

1. Implement screenshot comparison:
   ```python
   def test_main_window_appearance(app, qtbot, main_window):
       """Test main window matches reference screenshot"""
       # Capture screenshot
       pixmap = main_window.grab()
       pixmap.save("current_main_window.png")

       # Compare with reference image
       # Use image comparison library or manual verification
   ```

2. Create reference screenshots for key UI states

## Running Tests

```bash
# Run all UI tests
pytest tests/ui/

# Run specific test category
pytest tests/ui/test_dark_mode.py

# Run with coverage report
pytest tests/ui/ --cov=src/aetherra/ui
```

## Continuous Integration

- Integrate UI tests with CI pipeline
- Generate UI test reports
- Compare screenshots across commits
- Block PRs that break UI standards

## Documentation

- Document UI test results
- Maintain visual regression reports
- Update style guide based on test findings
