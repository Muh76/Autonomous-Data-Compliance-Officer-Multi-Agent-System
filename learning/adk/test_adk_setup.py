"""Test script to verify ADK setup and installation."""

import sys
import importlib

def test_adk_import():
    """Test if ADK can be imported."""
    try:
        import google.adk
        print("✓ ADK imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import ADK: {e}")
        return False

def test_agent_classes():
    """Test if ADK agent classes can be imported."""
    try:
        from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent, Coordinator
        print("✓ Agent classes imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import agent classes: {e}")
        print("  Note: This might be expected if ADK structure differs")
        return False

def test_tools():
    """Test if ADK tools can be imported."""
    try:
        from google.adk.tools import Tool
        print("✓ Tool classes imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import tool classes: {e}")
        print("  Note: This might be expected if ADK structure differs")
        return False

def main():
    """Run all tests."""
    print("Testing ADK Setup...")
    print("=" * 50)
    
    results = []
    results.append(("ADK Import", test_adk_import()))
    results.append(("Agent Classes", test_agent_classes()))
    results.append(("Tools", test_tools()))
    
    print("=" * 50)
    print("\nTest Results:")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  {name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed! ADK is properly set up.")
        return 0
    else:
        print("\n⚠ Some tests failed. Please check ADK installation.")
        print("\nNote: If ADK structure differs from expected, you may need to:")
        print("  1. Check ADK documentation for correct import paths")
        print("  2. Verify ADK version compatibility")
        print("  3. Review ADK installation instructions")
        return 1

if __name__ == "__main__":
    sys.exit(main())

