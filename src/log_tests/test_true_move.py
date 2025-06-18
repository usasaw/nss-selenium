# tests/test_true_move.py

import pytest
from src.browser_test.true_move import run_test

def test_run_test():
    result = run_test()
    print("📋 รายงานผล:", result)
    assert "Test passed" in result

