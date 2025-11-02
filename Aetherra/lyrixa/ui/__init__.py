#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""
Lyrixa UI Expression and Interaction Layer
==========================================

Provides the expressive interface for Lyrixa's interactive personality,
including emotion management, visual expressions, and real-time feedback.
"""

from .expression_manager import ExpressionManager, ExpressionState

__all__ = ["ExpressionManager", "ExpressionState"]
