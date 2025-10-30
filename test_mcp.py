"""Test script for MCP server.

This script tests the MCP server by directly importing and calling it.
"""

import asyncio
import sys
from pathlib import Path

# Add server directory to path
sys.path.insert(0, str(Path(__file__).parent / "server"))

import mcp.types as types
from server.main import mcp, widgets, WIDGETS_BY_ID


async def test_list_tools():
    """Test listing available tools."""
    print("=" * 60)
    print("1. Testing Tools List")
    print("=" * 60)

    from server.main import _list_tools
    tools = await _list_tools()

    print(f"\n✓ Found {len(tools)} tool(s):\n")
    for tool in tools:
        print(f"  • {tool.name}")
        print(f"    Title: {tool.title}")
        print(f"    Description: {tool.description}")
        print(f"    Input Schema: {tool.inputSchema}")
        print()

    return tools


async def test_list_resources():
    """Test listing available resources."""
    print("=" * 60)
    print("2. Testing Resources List")
    print("=" * 60)

    from server.main import _list_resources
    resources = await _list_resources()

    print(f"\n✓ Found {len(resources)} resource(s):\n")
    for resource in resources:
        print(f"  • {resource.name}")
        print(f"    URI: {resource.uri}")
        print(f"    MIME Type: {resource.mimeType}")
        print(f"    Description: {resource.description}")
        print()

    return resources


async def test_call_tool():
    """Test calling a tool."""
    print("=" * 60)
    print("3. Testing Tool Call (example-widget)")
    print("=" * 60)

    # Create tool call request
    request = types.CallToolRequest(
        params=types.CallToolRequestParams(
            name="example-widget",
            arguments={"message": "Hello from Python Test!"}
        )
    )

    # Call the handler
    from server.main import _call_tool_request
    result = await _call_tool_request(request)

    print("\n✓ Tool executed successfully\n")

    # ServerResult contains the actual result
    # Access it through the types.CallToolResult that was passed
    if hasattr(result, 'root'):
        tool_result = result.root
    else:
        # Try to get the result directly
        tool_result = result

    print("Response Content:")
    if hasattr(tool_result, 'content'):
        for content in tool_result.content:
            if hasattr(content, 'text'):
                print(f"  {content.text}")

    if hasattr(tool_result, 'structuredContent'):
        print(f"\nStructured Content:")
        print(f"  {tool_result.structuredContent}")

    if hasattr(tool_result, '_meta') and tool_result._meta:
        print(f"\nWidget Metadata:")
        widget_meta = tool_result._meta.get("openai.com/widget", {})
        if widget_meta:
            resource = widget_meta.get("resource", {})
            print(f"  URI: {resource.get('uri')}")
            print(f"  MIME Type: {resource.get('mimeType')}")
            print(f"  Title: {resource.get('title')}")
            html_text = resource.get('text', '')
            print(f"  HTML Size: {len(html_text)} bytes")

    return result


async def test_read_resource():
    """Test reading a resource."""
    print("=" * 60)
    print("4. Testing Resource Read")
    print("=" * 60)

    # Create resource read request
    request = types.ReadResourceRequest(
        params=types.ReadResourceRequestParams(
            uri="ui://widget/example.html"
        )
    )

    # Call the handler
    from server.main import _handle_read_resource
    result = await _handle_read_resource(request)

    print("\n✓ Resource read successfully\n")

    # Extract and display result
    if hasattr(result, 'root'):
        read_result = result.root
    else:
        read_result = result

    if hasattr(read_result, 'contents'):
        for content in read_result.contents:
            print(f"URI: {content.uri}")
            print(f"MIME Type: {content.mimeType}")
            print(f"HTML Size: {len(content.text)} bytes")
            print(f"\nHTML Preview (first 300 chars):")
            print(content.text[:300] + "...")

    return result


async def test_widget_loading():
    """Test that widgets are loaded correctly."""
    print("=" * 60)
    print("5. Testing Widget Loading")
    print("=" * 60)

    print(f"\n✓ Loaded {len(widgets)} widget(s):\n")

    for widget in widgets:
        print(f"  • {widget.identifier}")
        print(f"    Title: {widget.title}")
        print(f"    Template URI: {widget.template_uri}")
        print(f"    HTML Size: {len(widget.html)} bytes")
        print(f"    Has HTML: {'✓' if widget.html else '✗'}")
        print()


async def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("MCP Server Test Suite")
    print("=" * 60)
    print()

    try:
        # Test widget loading
        await test_widget_loading()

        # Test tools list
        await test_list_tools()

        # Test resources list
        await test_list_resources()

        # Test tool call
        await test_call_tool()

        # Test resource read
        await test_read_resource()

        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        print()

    except Exception as e:
        print(f"\n✗ Test failed with error:")
        print(f"  {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
