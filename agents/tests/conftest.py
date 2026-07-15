import sys
from unittest.mock import MagicMock

# Create a single global mock for google.generativeai to prevent cross-test import conflicts
mock_genai = MagicMock()
sys.modules["google.generativeai"] = mock_genai
