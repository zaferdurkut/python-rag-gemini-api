#!/usr/bin/env python3
"""
Test runner script for the RAG system
"""

import subprocess
import sys
import os


def run_pytest():
    """Run pytest tests."""
    print("🧪 Running pytest tests...")
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", "tests/", "-v", "--tb=short"],
            cwd=os.path.dirname(__file__),
            capture_output=True,
            text=True,
        )
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running pytest: {e}")
        return False


def run_embedding_tests():
    """Run embedding tests manually."""
    print("🧪 Running embedding tests manually...")
    try:
        result = subprocess.run(
            ["python", "tests/test_embeddings.py"],
            cwd=os.path.dirname(__file__),
            capture_output=True,
            text=True,
        )
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running embedding tests: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 Starting Test Suite\n")

    # Run pytest tests
    pytest_success = run_pytest()
    print(f"\nPytest Results: {'✅ PASSED' if pytest_success else '❌ FAILED'}")

    # Run embedding tests manually
    embedding_success = run_embedding_tests()
    print(f"Embedding Tests: {'✅ PASSED' if embedding_success else '❌ FAILED'}")

    # Summary
    print("\n📋 Test Summary:")
    print(f"Pytest Tests: {'✅ PASSED' if pytest_success else '❌ FAILED'}")
    print(f"Embedding Tests: {'✅ PASSED' if embedding_success else '❌ FAILED'}")

    if pytest_success and embedding_success:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️  Some tests failed.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
