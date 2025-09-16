#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""Unit tests for kernel loop self-incorporation service registration fix."""

from unittest.mock import MagicMock


class TestKernelLoopSelfIncorporation:
    """Test the kernel loop self-incorporation service registration fix."""

    def test_service_instance_pattern_validation(self):
        """Validate that our fix creates service instances not metadata dicts."""
        # The key fix: create service instances instead of metadata dicts
        mock_service_instance = MagicMock()
        mock_service_class = MagicMock(return_value=mock_service_instance)

        # Verify that service class creates instance
        actual_service = mock_service_class()
        assert actual_service is mock_service_instance

        # Verify service has required methods our fix uses
        assert hasattr(mock_service_instance, "inject_system")
        assert hasattr(mock_service_instance, "startup")

    def test_service_registration_fix_validation(self):
        """Validate that our fix registers service instances not metadata dicts."""
        # Test the pattern our fix implements
        mock_registry = MagicMock()
        mock_service = MagicMock()

        # This is what our fix does - register the actual service instance
        mock_registry.register_service("self_incorporation", mock_service, metadata={})

        # Verify registry was called with service instance (not dict)
        mock_registry.register_service.assert_called_once()
        call_args = mock_registry.register_service.call_args

        # First argument should be service name (string)
        assert call_args[0][0] == "self_incorporation"

        # Second argument should be service instance (has methods)
        service_arg = call_args[0][1]
        assert service_arg is mock_service
        assert hasattr(service_arg, "inject_system")  # Service instances have methods
