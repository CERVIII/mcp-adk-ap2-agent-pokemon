"""
Configuration for pytest
"""
import sys
import os
from pathlib import Path

# Add ap2-integration to path
project_root = Path(__file__).parent.parent
ap2_path = project_root / "ap2-integration"
sys.path.insert(0, str(ap2_path))

# Configure test environment
os.environ["TESTING"] = "1"
