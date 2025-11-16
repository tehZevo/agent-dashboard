#!/usr/bin/env python3
"""
Test script for MCP Server
Simulates MCP client interactions to test server functionality
"""
import json
import subprocess
import asyncio
from pathlib import Path

async def test_mcp_server():
    """Test the MCP server by simulating client interactions"""

    print("Testing MCP Server functionality...\n")

    # Test data
    test_results = []

    # Start the MCP server as a subprocess
    process = subprocess.Popen(
        ['python3', 'mcp_server.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=Path(__file__).parent
    )

    try:
        # Send initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }

        print("1. Testing MCP server initialization...")
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()

        # Read response (with timeout)
        try:
            response_line = await asyncio.wait_for(
                asyncio.to_thread(process.stdout.readline),
                timeout=5.0
            )
            response = json.loads(response_line)
            if "result" in response:
                print("   ✓ Server initialized successfully")
                test_results.append(("Initialize", True))
            else:
                print("   ✗ Server initialization failed")
                test_results.append(("Initialize", False))
        except asyncio.TimeoutError:
            print("   ✗ Server initialization timed out")
            test_results.append(("Initialize", False))

        # Send initialized notification
        initialized_notif = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        process.stdin.write(json.dumps(initialized_notif) + "\n")
        process.stdin.flush()

        # Test tools/list
        print("\n2. Testing tools/list...")
        list_tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }

        process.stdin.write(json.dumps(list_tools_request) + "\n")
        process.stdin.flush()

        try:
            response_line = await asyncio.wait_for(
                asyncio.to_thread(process.stdout.readline),
                timeout=5.0
            )
            response = json.loads(response_line)
            if "result" in response and "tools" in response["result"]:
                tools = response["result"]["tools"]
                print(f"   ✓ Found {len(tools)} tools:")
                for tool in tools:
                    print(f"      - {tool['name']}")
                test_results.append(("List Tools", True))
            else:
                print("   ✗ Failed to list tools")
                test_results.append(("List Tools", False))
        except asyncio.TimeoutError:
            print("   ✗ Tools list timed out")
            test_results.append(("List Tools", False))

        # Test set_agent_status
        print("\n3. Testing set_agent_status tool...")
        set_status_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "set_agent_status",
                "arguments": {
                    "agent_id": "test-mcp-agent",
                    "status_message": "Testing MCP server",
                    "task_status": "working",
                    "team": "Test Team"
                }
            }
        }

        process.stdin.write(json.dumps(set_status_request) + "\n")
        process.stdin.flush()

        try:
            response_line = await asyncio.wait_for(
                asyncio.to_thread(process.stdout.readline),
                timeout=5.0
            )
            response = json.loads(response_line)
            if "result" in response and "content" in response["result"]:
                print("   ✓ Agent status set successfully")
                print(f"      {response['result']['content'][0]['text'][:80]}...")
                test_results.append(("Set Agent Status", True))
            else:
                print("   ✗ Failed to set agent status")
                test_results.append(("Set Agent Status", False))
        except asyncio.TimeoutError:
            print("   ✗ Set agent status timed out")
            test_results.append(("Set Agent Status", False))

        # Test get_agent_status
        print("\n4. Testing get_agent_status tool...")
        get_status_request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "get_agent_status",
                "arguments": {
                    "agent_id": "test-mcp-agent"
                }
            }
        }

        process.stdin.write(json.dumps(get_status_request) + "\n")
        process.stdin.flush()

        try:
            response_line = await asyncio.wait_for(
                asyncio.to_thread(process.stdout.readline),
                timeout=5.0
            )
            response = json.loads(response_line)
            if "result" in response and "content" in response["result"]:
                print("   ✓ Agent status retrieved successfully")
                test_results.append(("Get Agent Status", True))
            else:
                print("   ✗ Failed to get agent status")
                test_results.append(("Get Agent Status", False))
        except asyncio.TimeoutError:
            print("   ✗ Get agent status timed out")
            test_results.append(("Get Agent Status", False))

        # Test list_all_agents
        print("\n5. Testing list_all_agents tool...")
        list_agents_request = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "list_all_agents",
                "arguments": {}
            }
        }

        process.stdin.write(json.dumps(list_agents_request) + "\n")
        process.stdin.flush()

        try:
            response_line = await asyncio.wait_for(
                asyncio.to_thread(process.stdout.readline),
                timeout=5.0
            )
            response = json.loads(response_line)
            if "result" in response and "content" in response["result"]:
                agents_data = json.loads(response["result"]["content"][0]["text"])
                print(f"   ✓ Listed {len(agents_data)} agents")
                test_results.append(("List All Agents", True))
            else:
                print("   ✗ Failed to list agents")
                test_results.append(("List All Agents", False))
        except asyncio.TimeoutError:
            print("   ✗ List agents timed out")
            test_results.append(("List All Agents", False))

    finally:
        # Terminate the server
        process.terminate()
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()

    # Print summary
    print("\n" + "="*50)
    print("MCP Server Test Summary")
    print("="*50)

    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)

    for test_name, result in test_results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n✅ All MCP server tests passed!")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(test_mcp_server())
    exit(0 if success else 1)
