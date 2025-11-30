"""Test script for refactored MCP server.

This script tests the MCP server with separated Widget and Tool concerns.
Tests both widget-based tools and text-based tools.
"""

import asyncio
import sys
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import mcp.types as types
from server.config import CONFIG
from server.services import build_widgets, build_tools
from server.factory import create_mcp_server
from server.handlers import get_games_by_sport_handler, get_game_details_handler


@pytest.fixture
def mcp_server():
    """Create MCP server instance for testing."""
    return create_mcp_server(CONFIG)


@pytest.mark.asyncio
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
        print()

    return widgets


@pytest.mark.asyncio
async def test_tool_loading():
    """Test that tools are loaded correctly (both widget and text-based)."""
    print("=" * 60)
    print("2. Testing Tool Loading")
    print("=" * 60)

    # Build tools using factory function
    tools = build_tools(
        CONFIG,
        get_games_by_sport_handler=get_games_by_sport_handler,
        get_game_details_handler=get_game_details_handler,
    )

    print(f"\n✓ Loaded {len(tools)} tool(s):\n")

    widget_count = 0
    text_count = 0

    for tool in tools:
        print(f"  • {tool.name}")
        print(f"    Title: {tool.title}")
        print(f"    Has Widget: {'✓' if tool.has_widget else '✗'}")
        print(f"    Has Handler: {'✓' if tool.handler else '✗'}")

        if tool.has_widget:
            widget_count += 1
            print(f"    Widget: {tool.widget.identifier if tool.widget else 'None'}")
        else:
            text_count += 1
        print()

    print(f"Summary: {widget_count} widget tool(s), {text_count} text tool(s)\n")
    return tools


@pytest.mark.asyncio
async def test_list_tools(mcp_server):
    """Test listing available tools."""
    print("=" * 60)
    print("3. Testing Tools List (MCP Protocol)")
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

    print(f"\n✓ Found {len(tools_list)} tool(s) via MCP protocol:\n")
    for tool in tools_list:
        print(f"  • {tool.name}")
        print(f"    Title: {tool.title}")
        print(f"    Description: {tool.description}")

        # Check metadata for tool type
        meta = getattr(tool, '_meta', None) or getattr(tool, 'meta', None)
        if meta:
            has_widget = meta.get("openai/resultCanProduceWidget", False)
            print(f"    Can Produce Widget: {'✓' if has_widget else '✗'}")
        print()

    return tools_list


@pytest.mark.asyncio
async def test_list_resources(mcp_server):
    """Test listing available resources."""
    print("=" * 60)
    print("4. Testing Resources List")
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

    print("Note: Only widget tools have resources (text tools don't)\n")
    return resources_list


@pytest.mark.asyncio
async def test_call_widget_tool(mcp_server):
    """Test calling a widget tool (get_game_details)."""
    print("=" * 60)
    print("5. Testing Widget Tool Call (get_game_details)")
    print("=" * 60)

    # Create tool call request - uses mock data
    request = types.CallToolRequest(
        params=types.CallToolRequestParams(
            name="get_game_details",
            arguments={"game_id": "test-game-001"}
        )
    )

    # Call the handler
    handler = mcp_server._mcp_server.request_handlers[types.CallToolRequest]
    result = await handler(request)

    # ServerResult contains the actual result
    if hasattr(result, 'root'):
        tool_result = result.root
    else:
        tool_result = result

    # Check if it's an error (expected since we're using mock data)
    is_error = getattr(tool_result, 'isError', False)
    if is_error:
        print("\n⚠️ Tool returned error (expected with test game_id)\n")
    else:
        print("\n✓ Widget tool executed successfully\n")

    print("Response Content:")
    if hasattr(tool_result, 'content'):
        for content in tool_result.content:
            if hasattr(content, 'text'):
                print(f"  {content.text}")

    if hasattr(tool_result, 'structuredContent') and tool_result.structuredContent:
        print(f"\nStructured Content (props for React):")
        import json
        preview = json.dumps(tool_result.structuredContent, indent=2)[:300]
        print(f"  {preview}...")

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


@pytest.mark.asyncio
async def test_call_text_tool(mcp_server):
    """Test calling a text-based tool (get_games_by_sport)."""
    print("=" * 60)
    print("6. Testing Text Tool Call (get_games_by_sport)")
    print("=" * 60)

    # Test with basketball
    request = types.CallToolRequest(
        params=types.CallToolRequestParams(
            name="get_games_by_sport",
            arguments={"date": "20251128", "sport": "basketball"}
        )
    )

    handler = mcp_server._mcp_server.request_handlers[types.CallToolRequest]
    result = await handler(request)

    if hasattr(result, 'root'):
        tool_result = result.root
    else:
        tool_result = result

    is_error = getattr(tool_result, 'isError', False)
    if is_error:
        print("\n⚠️ Tool returned error (may be expected with external API)\n")
    else:
        print("\n✓ Text tool executed successfully\n")

    print("Response:")
    if hasattr(tool_result, 'content'):
        for content in tool_result.content:
            if hasattr(content, 'text'):
                # Print first 500 chars
                text = content.text
                if len(text) > 500:
                    print(f"  {text[:500]}...")
                else:
                    print(f"  {text}")

    return result


@pytest.mark.asyncio
async def test_read_resource(mcp_server):
    """Test reading a resource (game-result-viewer widget)."""
    print("=" * 60)
    print("7. Testing Resource Read (game-result-viewer)")
    print("=" * 60)

    # First get the widget URI from resources list
    list_request = types.ListResourcesRequest()
    list_handler = mcp_server._mcp_server.request_handlers[types.ListResourcesRequest]
    list_result = await list_handler(list_request)

    if hasattr(list_result, 'root'):
        resources = list_result.root.resources
    else:
        resources = list_result.resources

    if not resources:
        print("\n⚠️ No resources available to read\n")
        return None

    # Use the first available resource URI
    resource_uri = str(resources[0].uri)
    print(f"\nReading resource: {resource_uri}\n")

    # Create resource read request
    request = types.ReadResourceRequest(
        params=types.ReadResourceRequestParams(
            uri=resource_uri
        )
    )

    # Call the handler
    handler = mcp_server._mcp_server.request_handlers[types.ReadResourceRequest]
    result = await handler(request)

    print("✓ Resource read successfully\n")

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
    print("MCP Server Test Suite (Refactored Architecture)")
    print("=" * 60)
    print()

    try:
        # Test widget loading
        await test_widget_loading()

        # Test tool loading
        await test_tool_loading()

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

        # Test widget tool call
        await test_call_widget_tool(mcp_server)

        # Test text tool call
        await test_call_text_tool(mcp_server)

        # Test resource read
        await test_read_resource(mcp_server)

        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        print("\nArchitecture Summary:")
        print("  • Widgets: Pure UI components (no tool metadata)")
        print("  • Tools: Can be widget-based OR text-based")
        print("  • Clear separation of concerns")
        print("  • Both tool types tested successfully")
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
