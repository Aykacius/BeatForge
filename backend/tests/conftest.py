"""Test configuration."""

import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Test database URL
os.environ["DATABASE_URL"] = "sqlite:///test.db"
os.environ["DEBUG"] = "true"
