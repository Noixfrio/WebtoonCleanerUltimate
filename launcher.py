import unittest
import sys
import os

# Ensure the root directory is in sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from launcher.main import main

if __name__ == "__main__":
    main()
