"""
Enhancement Controller Module
This module provides UI enhancement functionalities for the Aetherra project.
"""


class UIEnhancer:
    def __init__(self):
        self.enhancements = []

    def add_enhancement(self, enhancement):
        """Add a new UI enhancement."""
        self.enhancements.append(enhancement)

    def apply_enhancements(self, ui_component):
        """Apply all enhancements to the given UI component."""
        for enhancement in self.enhancements:
            enhancement(ui_component)


# Example enhancement function
def example_enhancement(ui_component):
    """An example enhancement that modifies a UI component."""
    ui_component.setStyleSheet("background-color: lightblue;")


# Module-level instance
ui_enhancer = UIEnhancer()
ui_enhancer.add_enhancement(example_enhancement)
