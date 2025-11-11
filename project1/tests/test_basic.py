"""
Basic tests for Project 1.
"""

import pytest
from project1 import __version__


def test_version():
    """Test that version is defined."""
    assert __version__ is not None
    assert isinstance(__version__, str)


def test_import():
    """Test that package can be imported."""
    import project1
    assert project1 is not None


# Add more tests here
