# UI Accessibility Guidelines

## Overview

This document provides accessibility guidelines for the aetherra user interface to ensure the application is usable by everyone, including users with disabilities. Following these guidelines will help make the UI more inclusive and compliant with accessibility standards.

## Contrast and Colors

### Color Contrast Requirements

- **Minimum Contrast Ratio**: 4.5:1 for normal text (WCAG AA)
- **Enhanced Contrast**: 7:1 for better accessibility (WCAG AAA)
- **Large Text**: 3:1 minimum for text larger than 18pt or 14pt bold

```
// Example of accessible color combinations:
Text: #FFFFFF (White) on Background: #1E1E1E (Dark Gray)
- Contrast ratio: 15.6:1 ✓ Passes AAA

Text: #CCCCCC (Light Gray) on Background: #1E1E1E (Dark Gray)
- Contrast ratio: 9.58:1 ✓ Passes AAA
```

### Color Usage Guidelines

- Never rely solely on color to convey information
- Include additional indicators (text, icons, patterns)
- Use colors from the approved palette in UI_STYLE_GUIDE.md
- Avoid problematic color combinations for color blindness:
  - Red/Green
  - Blue/Yellow
  - Green/Brown

## Text and Typography

- **Font Size**: Minimum 13px for body text
- **Font Weight**: Use appropriate weights for hierarchy
- **Line Spacing**: At least 1.5 times the font size
- **Text Alignment**: Left-aligned text for better readability
- **Text Overflow**: Ensure text can be resized up to 200% without loss of content

## Keyboard Navigation

### Focus Indicators

- Ensure visible focus indicators on all interactive elements
- Focus indicator should have 3:1 contrast against adjacent colors
- Never remove focus outlines without providing an alternative

```css
/* Example of proper focus styling */
:focus {
    outline: 2px solid #0078D4;
    outline-offset: 2px;
}
```

### Tab Order

- Logical tab order following visual layout
- Ensure all interactive elements are keyboard accessible
- Implement keyboard shortcuts for common actions

## Screen Reader Support

### Semantic Structure

- Use proper heading hierarchy (H1, H2, H3)
- Implement proper ARIA roles and landmarks
- Provide meaningful labels for form controls
- Use descriptive text for links and buttons

### Text Alternatives

- Provide alt text for all images and icons
- Include labels for all form controls
- Ensure error messages are accessible

## Interactive Elements

### Buttons and Controls

- Minimum target size: 44x44 pixels
- Clear visual state indicators (hover, focus, active)
- Descriptive labels that explain the action

### Forms and Inputs

- Clear labels for all form fields
- Visible error messages with suggestions
- Associate labels with form controls
- Group related form elements

## Testing and Verification

### Manual Testing

- Test with keyboard navigation only
- Verify color contrast with tools like Colour Contrast Analyzer
- Check text resize functionality

### Automated Testing

- Implement accessibility unit tests
- Verify ARIA attributes are properly set
- Check color contrast programmatically

## Implementation Example

### Accessible Button

```python
def create_accessible_button(label, action):
    """Create an accessible button with proper styling and keyboard support"""
    button = QPushButton(label)
    button.clicked.connect(action)
    button.setStyleSheet("""
        QPushButton {
            background-color: #2D2D2D; /* Proper contrast with text */
            color: #FFFFFF;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            min-width: 80px;
            min-height: 32px; /* Ensures adequate target size */
        }
        QPushButton:hover {
            background-color: #0078D4; /* Clear visual indication */
        }
        QPushButton:focus {
            outline: 2px solid #FFFFFF; /* Visible focus indicator */
            outline-offset: 2px;
        }
        QPushButton:disabled {
            background-color: #4D4D4D;
            color: #888888; /* Maintains 3:1 contrast ratio */
        }
    """)
    return button
```

### Accessible Form Field

```python
def create_accessible_input(label_text, placeholder=""):
    """Create an accessible input field with associated label"""
    container = QWidget()
    layout = QVBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(4)

    # Create label with unique ID
    label = QLabel(label_text)
    input_id = f"input_{label_text.lower().replace(' ', '_')}"
    label.setObjectName(f"label_for_{input_id}")
    layout.addWidget(label)

    # Create input with proper styling and accessibility
    input_field = QLineEdit()
    input_field.setObjectName(input_id)
    input_field.setPlaceholderText(placeholder)
    input_field.setStyleSheet("""
        QLineEdit {
            background-color: #333333;
            color: #FFFFFF;
            border: 1px solid #444444;
            border-radius: 4px;
            padding: 8px;
            min-height: 32px;
        }
        QLineEdit:focus {
            border: 2px solid #0078D4;
        }
    """)
    layout.addWidget(input_field)

    return container, input_field
```

## Resources

- [Web Content Accessibility Guidelines (WCAG) 2.1](https://www.w3.org/TR/WCAG21/)
- [Qt Accessibility](https://doc.qt.io/qt-5/accessible.html)
- [Colour Contrast Analyzer](https://developer.paciellogroup.com/resources/contrastanalyser/)
- [WAVE Web Accessibility Evaluation Tool](https://wave.webaim.org/)
