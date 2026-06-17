import sys
import os

# Add the repository root to python path to ensure imports work seamlessly when compiled
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.gui.app import launch

if __name__ == "__main__":
    launch()
