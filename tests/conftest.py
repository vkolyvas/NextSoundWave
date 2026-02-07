"""Pytest configuration and fixtures."""

import pytest


# Register custom markers
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "network: mark test as requiring network access"
    )
