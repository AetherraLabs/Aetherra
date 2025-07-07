# aetherra UI Style Guide

## Overview

This document defines the standardized UI styling guidelines for the aetherra project. Following these guidelines ensures consistency across all UI components and improves accessibility, readability, and maintainability.

## Color Palette

### Dark Theme (Default)

- **Background Colors**
  - Primary Background: `#1e1e1e`
  - Secondary Background: `#252525`
  - Tertiary Background: `#333333`
  - Control Background: `#2d2d2d`

- **Text Colors**
  - Primary Text: `#ffffff`
  - Secondary Text: `#cccccc`
  - Disabled Text: `#888888`

- **Accent Colors**
  - Primary Accent: `#0078d4` (Blue)
  - Hover Accent: `#106ebe` (Lighter Blue)
  - Success: `#107c10` (Green)
  - Warning: `#d8a629` (Orange/Yellow)
  - Error: `#d13438` (Red)
  - Info: `#0078d4` (Blue)

### Light Theme (Optional)

- **Background Colors**
  - Primary Background: `#f8f8f8`
  - Secondary Background: `#ffffff`
  - Tertiary Background: `#f0f0f0`
  - Control Background: `#f5f5f5`

- **Text Colors**
  - Primary Text: `#252525`
  - Secondary Text: `#555555`
  - Disabled Text: `#888888`

- **Accent Colors**
  - Primary Accent: `#0078d4` (Blue)
  - Hover Accent: `#106ebe` (Lighter Blue)
  - Success: `#107c10` (Green)
  - Warning: `#d8a629` (Orange/Yellow)
  - Error: `#d13438` (Red)
  - Info: `#0078d4` (Blue)

## Typography

- **Fonts**
  - UI Font: `'Segoe UI', Arial, sans-serif`
  - Code Font: `'Consolas', 'Courier New', monospace`

- **Font Sizes**
  - Window Title: 16px
  - Headers: 14px
  - Body Text: 13px
  - Small Text: 12px
  - Code: 13px

- **Font Weights**
  - Headers: Bold (700)
  - Regular Text: Normal (400)
  - Emphasized: Semi-bold (600)

## Layout

- **Spacing**
  - Default Margin: 8px
  - Compact Margin: 4px
  - Content Padding: 8px
  - Control Padding: 8px
  - Vertical Spacing Between Elements: 8px

- **Control Sizes**
  - Button Height: 32px
  - Input Height: 32px
  - Toolbar Height: 36px
  - Tab Height: 32px

- **Corner Radius**
  - Standard UI Elements: 6px
  - Small Controls (buttons, inputs): 4px
  - Chat Messages: 0px (flat design)

## Icons and Visual Elements

- **Status Indicators**
  - Success: `[DONE]`, `[SUCCESS]`, or "Success:"
  - Error: `[FAIL]`, `[ERROR]`, or "Error:"
  - Warning: `[WARN]` or "Warning:"
  - Information: `[INFO]` or "Info:"
  - Pending: `[WAIT]` or "Pending..."
  - Running: `[RUN]` or "Running..."
  - Retry: `[RETRY]` or "Retrying..."
  - Cancelled: `[STOP]` or "Cancelled"

## Chat Area Styling

- **Message Display**
  - Flat design (no bubbles)
  - Clear separation between messages (8px margins)
  - User messages: Aligned left, no background
  - Assistant messages: Aligned left, no background
  - System messages: Italicized, secondary text color
  - Message metadata: Small font size (12px), secondary text color
  - Code blocks: Monospaced font, syntax highlighting, light background (#252525)

- **Input Area**
  - Clear visual separation from message history
  - Standard input height (32px for single line, flexible for multi-line)
  - Send button aligned right
  - Placeholder text in secondary color

## Buttons and Controls

- **Button Types**
  - Primary: Blue (#0078d4) with white text
  - Secondary: Dark gray (#333333) with white text
  - Success: Green (#107c10) with white text
  - Danger: Red (#d13438) with white text
  - Disabled: Gray (#555555) with darker gray text

- **Control States**
  - Default: Standard styling
  - Hover: Slightly lighter version of control color
  - Pressed: Slightly darker version of control color
  - Focused: Primary accent color border (2px)
  - Disabled: Gray with lower opacity

## Widget Styling

- **Text Editors/Fields**
  - Background: Secondary background (#252525)
  - Border: 1px solid #404040
  - Focused Border: 2px solid primary accent (#0078d4)
  - Font: UI font or code font for code editors
  - Line Height: 1.2em for readability

- **Lists and Trees**
  - Item Height: 24px (standard), 20px (compact)
  - Selected Item: Primary accent background
  - Alternating Rows: Subtle difference in background (optional)

- **Tabs**
  - Active Tab: Stands out with subtle border and background change
  - Hover Tab: Slightly lighter background
  - Close Button: Small, visible on hover

## Accessibility Guidelines

- **Color Contrast**
  - Text elements must maintain a minimum contrast ratio of 4.5:1
  - Important UI elements should have higher contrast (7:1 if possible)
  - Never rely solely on color to convey information

- **Keyboard Navigation**
  - All interactive elements must be focusable via keyboard
  - Tab order should be logical and follow visual layout
  - Keyboard shortcuts should be provided for common actions

- **Screen Reader Support**
  - All UI elements should have appropriate labels
  - Complex widgets should include ARIA attributes
  - Purely decorative elements should be hidden from screen readers

## Implementation Notes

This style guide is implemented in the following ways:

1. **Base StyleSheet**: A centralized Qt stylesheet that defines the core styling
2. **Widget-Specific Styling**: Additional styling for specialized widgets
3. **Programmatic Application**: Code-based styling for complex or dynamic elements

Refer to `get_dark_theme()` in the `LyrixaWindow` class for the core implementation of these guidelines.
