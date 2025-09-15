#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Minimal FlowLayout for wrapping PluginCards.

Adapted conceptually from Qt flow layout examples (public domain / examples),
implemented lightly to avoid external dependencies. Places child widgets
left-to-right then wraps based on available width.
"""

from __future__ import annotations

from PySide6.QtCore import QPoint, QRect, QSize
from PySide6.QtWidgets import QLayout, QLayoutItem, QSizePolicy, QWidget


class FlowLayout(QLayout):
    def __init__(
        self, parent: QWidget | None = None, margin: int = 6, spacing: int = 10
    ):
        super().__init__(parent)
        self._items: list[QLayoutItem] = []
        self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)

    def addItem(self, item: QLayoutItem):  # noqa: D401
        self._items.append(item)

    def count(self) -> int:  # noqa: D401
        return len(self._items)

    def itemAt(self, index: int):  # noqa: D401
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def takeAt(self, index: int):  # noqa: D401
        if 0 <= index < len(self._items):
            return self._items.pop(index)
        return None

    def expandingDirections(self):  # noqa: D401
        return 0

    def hasHeightForWidth(self) -> bool:  # noqa: D401
        return True

    def heightForWidth(self, width: int) -> int:  # noqa: D401
        return self._do_layout(QRect(0, 0, width, 0), test_only=True)

    def setGeometry(self, rect: QRect):  # noqa: D401
        super().setGeometry(rect)
        self._do_layout(rect, test_only=False)

    def sizeHint(self) -> QSize:  # noqa: D401
        return self.minimumSize()

    def minimumSize(self) -> QSize:  # noqa: D401
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        m = self.contentsMargins()
        size += QSize(m.left() + m.right(), m.top() + m.bottom())
        return size

    # Internal layout algorithm
    def _do_layout(self, rect: QRect, test_only: bool) -> int:
        x = rect.x()
        y = rect.y()
        line_height = 0
        space_x = self.spacing()
        space_y = self.spacing()
        m = self.contentsMargins()
        effective_width = rect.width() - (m.left() + m.right())

        for item in self._items:
            wid = item.widget()
            hint = item.sizeHint()
            if hint.width() > effective_width and effective_width > 0:
                # Force shrink if single card wider than area
                target_w = effective_width
            else:
                target_w = hint.width()

            next_x = x + target_w + space_x
            if next_x - rect.x() > effective_width and line_height > 0:
                x = rect.x()
                y = y + line_height + space_y
                next_x = x + target_w + space_x
                line_height = 0

            if not test_only and wid is not None:
                item.setGeometry(QRect(QPoint(x + m.left(), y + m.top()), hint))

            x = next_x
            line_height = max(line_height, hint.height())

        return y + line_height - rect.y() + m.top() + m.bottom()


__all__ = ["FlowLayout"]
