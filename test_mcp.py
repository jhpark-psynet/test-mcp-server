"""Test script for MCP server.

This script tests the MCP server by creating an instance and testing its handlers.
"""

import asyncio
import sys
from pathlib import Path

# Add server directory to path
sys.path.insert(0, str(Path(__file__).parent / "server"))

import mcp.types as types
from server.main import CONFIG, build_widgets, create_mcp_server


async def test_widget_loading():
    """Test that widgets are loaded correctly."""
    print("=" * 60)
    print("1. Testing Widget Loading")
    print("=" * 60)

    # Build widgets using factory function
    widgets = build_widgets(CONFIG)

    print(f"\n✓ Loaded {len(widgets)} widget(s):\n")

    for widget in widgets:
        print(f"  • {widget.identifier}")
        print(f"    Title: {widget.title}")
        print(f"    Template URI: {widget.template_uri}")
        print(f"    HTML Size: {len(widget.html)} bytes")
        print(f"    Has HTML: {'✓' if widget.html else '✗'}")
        print()

    return widgets


async def test_list_tools(mcp_server):
    """Test listing available tools."""
    print("=" * 60)
    print("2. Testing Tools List")
    print("=" * 60)

    # Get the list_tools handler
    handler = mcp_server._mcp_server.request_handlers.get(types.ListToolsRequest)
    if handler is None:
        # Try getting from registered handlers
        tools_list = []
        if hasattr(mcp_server._mcp_server, '_tool_manager'):
            tools_list = await mcp_server._mcp_server._tool_manager.list_tools()
        else:
            # Fallback: call the list_tools directly from server
            request = types.ListToolsRequest()
            result = await mcp_server._mcp_server.request_handlers[types.ListToolsRequest](request)
            if hasattr(result, 'root'):
                tools_list = result.root.tools
            else:
                tools_list = result.tools
    else:
        request = types.ListToolsRequest()
        result = await handler(request)
        if hasattr(result, 'root'):
            tools_list = result.root.tools
        else:
            tools_list = result.tools

    print(f"\n✓ Found {len(tools_list)} tool(s):\n")
    for tool in tools_list:
        print(f"  • {tool.name}")
        print(f"    Title: {tool.title}")
        print(f"    Description: {tool.description}")
        print()

    return tools_list


async def test_list_resources(mcp_server):
    """Test listing available resources."""
    print("=" * 60)
    print("3. Testing Resources List")
    print("=" * 60)

    request = types.ListResourcesRequest()
    handler = mcp_server._mcp_server.request_handlers[types.ListResourcesRequest]
    result = await handler(request)

    if hasattr(result, 'root'):
        resources_list = result.root.resources
    else:
        resources_list = result.resources

    print(f"\n✓ Found {len(resources_list)} resource(s):\n")
    for resource in resources_list:
        print(f"  • {resource.name}")
        print(f"    URI: {resource.uri}")
        print(f"    MIME Type: {resource.mimeType}")
        print(f"    Description: {resource.description}")
        print()

    return resources_list


async def test_call_tool(mcp_server):
    """Test calling a tool."""
    print("=" * 60)
    print("4. Testing Tool Call (example-widget)")
    print("=" * 60)

    # Create tool call request
    request = types.CallToolRequest(
        params=types.CallToolRequestParams(
            name="example-widget",
            arguments={"message": "Hello from Python Test!"}
        )
    )

    # Call the handler
    handler = mcp_server._mcp_server.request_handlers[types.CallToolRequest]
    result = await handler(request)

    print("\n✓ Tool executed successfully\n")

    # ServerResult contains the actual result
    if hasattr(result, 'root'):
        tool_result = result.root
    else:
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


async def test_read_resource(mcp_server):
    """Test reading a resource."""
    print("=" * 60)
    print("5. Testing Resource Read")
    print("=" * 60)

    # Create resource read request
    request = types.ReadResourceRequest(
        params=types.ReadResourceRequestParams(
            uri="ui://widget/example.html"
        )
    )

    # Call the handler
    handler = mcp_server._mcp_server.request_handlers[types.ReadResourceRequest]
    result = await handler(request)

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


async def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("MCP Server Test Suite")
    print("=" * 60)
    print()

    try:
        # Test widget loading
        await test_widget_loading()

        # Create MCP server instance
        print("=" * 60)
        print("Creating MCP Server Instance")
        print("=" * 60)
        mcp_server = create_mcp_server(CONFIG)
        print("\n✓ MCP server instance created\n")

        # Test tools list
        await test_list_tools(mcp_server)

        # Test resources list
        await test_list_resources(mcp_server)

        # Test tool call
        await test_call_tool(mcp_server)

        # Test resource read
        await test_read_resource(mcp_server)

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
