"""
Global pytest configuration for all tests
"""
import sys
import os
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent.parent
ap2_path = project_root / "ap2-integration"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(ap2_path))

# Configure test environment
os.environ["TESTING"] = "1"
os.environ["ENVIRONMENT"] = "test"
