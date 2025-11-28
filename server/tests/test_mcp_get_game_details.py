"""Test get_game_details MCP tool call."""
import asyncio
import json
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from server.config import Config
from server.factory.server_factory import create_mcp_server


async def test_get_game_details():
    """Test get_game_details tool via MCP."""
    cfg = Config()
    mcp = create_mcp_server(cfg)

    print("\n" + "="*60)
    print("Testing get_game_details MCP Tool")
    print("="*60)

    # List tools
    print("\n[1] Listing tools...")
    tools_list = await mcp.list_tools()
    print(f"Total tools: {len(tools_list)}")

    # Find get_game_details
    game_details_tool = None
    for tool in tools_list:
        if tool.name == "get_game_details":
            game_details_tool = tool
            break

    if not game_details_tool:
        print("❌ get_game_details tool not found!")
        return False

    print(f"\n✅ Found get_game_details tool")
    print(f"   Description: {game_details_tool.description[:100]}...")
    print(f"   Input schema: {json.dumps(game_details_tool.inputSchema, indent=2)}")

    # Call the tool
    print("\n[2] Calling get_game_details with game_id='OT2025313104237'...")
    try:
        result = await mcp.call_tool(
            name="get_game_details",
            arguments={"game_id": "OT2025313104237"}
        )

        print(f"\n✅ Tool call successful!")
        print(f"   Result type: {type(result)}")
        print(f"   Number of content items: {len(result.content)}")

        for i, content in enumerate(result.content):
            print(f"\n   Content [{i}]:")
            print(f"     Type: {content.type}")
            if hasattr(content, 'text'):
                print(f"     Text: {content.text[:200]}...")
            if hasattr(content, 'resource'):
                print(f"     Resource URI: {content.resource.uri}")
                print(f"     Resource mimeType: {content.resource.mimeType}")
                if hasattr(content.resource, 'structuredContent'):
                    print(f"     Has structuredContent: Yes")
                    if hasattr(content.resource.structuredContent, 'game_id'):
                        print(f"       Game ID: {content.resource.structuredContent.game_id}")
                    if hasattr(content.resource.structuredContent, 'game_info'):
                        print(f"       Game info: {content.resource.structuredContent.game_info}")

        return True

    except Exception as e:
        print(f"\n❌ Tool call failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run test."""
    success = await test_get_game_details()

    print("\n" + "="*60)
    if success:
        print("✅ Test PASSED")
    else:
        print("❌ Test FAILED")
    print("="*60)

    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
