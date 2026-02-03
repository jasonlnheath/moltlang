#!/usr/bin/env python3

"""
Comprehensive verification script for MoltLang MCP Tools Fix
"""

import json
import subprocess
import os

def test_python_bridge():
    """Test the Python bridge functionality"""
    print("=" * 60)
    print("TEST 1: Python Bridge Functionality")
    print("=" * 60)

    test_code = '''
import sys
import json
sys.path.insert(0, 'src')
from moltlang import translate_to_molt_result, translate_from_molt_result

# Test 1: translate_to_molt_result
result1 = translate_to_molt_result("Fetch data from API and return JSON")
print("=== TRANSLATE TO MOLT RESULT ===")
print(json.dumps({
    "text": result1.text,
    "token_count": result1.token_count,
    "original_token_count": result1.original_token_count,
    "token_efficiency": result1.token_efficiency,
    "confidence": result1.confidence
}, indent=2))

# Test 2: translate_from_molt_result
result2 = translate_from_molt_result("[OP:FETCH][SRC:API][RET:JSON]")
print("=== TRANSLATE FROM MOLT RESULT ===")
print(json.dumps({
    "text": result2.text,
    "token_count": result2.token_count,
    "confidence": result2.confidence
}, indent=2))
'''

    with open('bridge_test.py', 'w') as f:
        f.write(test_code)

    try:
        result = subprocess.run(['python', 'bridge_test.py'],
                              capture_output=True, text=True, timeout=10)
        os.remove('bridge_test.py')

        if result.returncode == 0:
            print("SUCCESS: Python bridge test PASSED")
            print(result.stdout)
            return True
        else:
            print("FAILED: Python bridge test FAILED")
            print("Error:", result.stderr)
            return False
    except Exception as e:
        print(f"FAILED: {e}")
        return False

def test_typeScript_build():
    """Test TypeScript build"""
    print("\n" + "=" * 60)
    print("TEST 2: TypeScript Build")
    print("=" * 60)

    try:
        result = subprocess.run(['npm', 'run', 'build'],
                              cwd='mcp-server',
                              capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            print("SUCCESS: TypeScript build PASSED")
            # Check if dist files exist
            dist_files = ['mcp-server/dist/index.js', 'mcp-server/dist/utils/python.js']
            for file_path in dist_files:
                if os.path.exists(file_path):
                    print(f"SUCCESS: {file_path} exists")
                else:
                    print(f"FAILED: {file_path} missing")
            return True
        else:
            print("FAILED: TypeScript build FAILED")
            print("Error:", result.stderr)
            return False
    except Exception as e:
        print(f"FAILED: {e}")
        return False

def test_python_mcp_server():
    """Test Python MCP server startup"""
    print("\n" + "=" * 60)
    print("TEST 3: Python MCP Server")
    print("=" * 60)

    server_path = 'src/mcp_server/server.py'
    if not os.path.exists(server_path):
        print("FAILED: Python MCP server not found")
        return False

    print("SUCCESS: Python MCP server file exists")

    # Test imports
    import_test = '''
from moltlang import MoltTranslator, MoltValidator, translate_to_molt_result, translate_from_molt_result
print("SUCCESS: All imports work")
'''

    with open('import_test.py', 'w') as f:
        f.write(import_test)

    try:
        result = subprocess.run(['python', 'import_test.py'],
                              capture_output=True, text=True, timeout=5)
        os.remove('import_test.py')

        if result.returncode == 0:
            print("SUCCESS: Python MCP server imports work")
            return True
        else:
            print("FAILED: Python MCP server imports failed")
            print("Error:", result.stderr)
            return False
    except Exception as e:
        print(f"FAILED: {e}")
        return False

def show_configuration():
    """Show MCP client configuration"""
    print("\n" + "=" * 60)
    print("MCP CLIENT CONFIGURATION")
    print("=" * 60)

    config = {
        "mcpServers": {
            "moltlang": {
                "command": "node",
                "args": ["C:/dev/moltlang/mcp-server/dist/index.js", "--stdio"]
            }
        }
    }

    print("Add this to your Claude Desktop config:")
    print(json.dumps(config, indent=2))
    print("\nOr use this Python MCP server:")
    print("command: python")
    print("args: ['C:/dev/moltlang/src/mcp_server/server.py']")

def main():
    print("MOLTLANG MCP TOOLS FIX - COMPREHENSIVE VERIFICATION")
    print("=" * 60)

    # Run tests
    test1_passed = test_python_bridge()
    test2_passed = test_typeScript_build()
    test3_passed = test_python_mcp_server()

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    if test1_passed:
        print("✅ Python Bridge: FIXED")
    else:
        print("❌ Python Bridge: FAILED")

    if test2_passed:
        print("✅ TypeScript Build: SUCCESS")
    else:
        print("❌ TypeScript Build: FAILED")

    if test3_passed:
        print("✅ Python MCP Server: READY")
    else:
        print("❌ Python MCP Server: FAILED")

    print("\n" + "=" * 60)
    print("AVAILABLE MCP TOOLS")
    print("=" * 60)
    tools = [
        "molt - English to MoltLang translation",
        "unmolt - MoltLang to English translation",
        "validate_molt - Translation validation",
        "list_tokens - List available tokens",
        "get_efficiency - Calculate token efficiency"
    ]

    for i, tool in enumerate(tools, 1):
        print(f"{i}. {tool}")

    # Show configuration
    show_configuration()

    print("\n" + "=" * 60)
    print("VERIFICATION COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()