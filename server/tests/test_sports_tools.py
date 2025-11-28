"""Test sports MCP tools."""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from server.handlers import get_games_by_sport_handler, get_game_details_handler


def test_get_games_by_sport():
    """Test get_games_by_sport handler."""
    print("\n" + "="*60)
    print("Testing get_games_by_sport")
    print("="*60)

    arguments = {
        "date": "20251118",
        "sport": "basketball"
    }

    try:
        result = get_games_by_sport_handler(arguments)
        print(f"\n✅ Success!")
        print(f"\nResult (first 800 chars):\n{result[:800]}")
        if len(result) > 800:
            print(f"\n... (total length: {len(result)} chars)")
        return True
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_game_details():
    """Test get_game_details handler."""
    print("\n" + "="*60)
    print("Testing get_game_details")
    print("="*60)

    arguments = {
        "game_id": "OT2025313104237"
    }

    try:
        result = get_game_details_handler(arguments)
        print(f"\n✅ Success!")
        print(f"\nResult type: {type(result)}")
        print(f"\nResult keys: {list(result.keys())}")
        print(f"\nGame ID: {result['game_id']}")
        print(f"\nGame Info:")
        for key, value in result['game_info'].items():
            print(f"  - {key}: {value}")
        print(f"\nTeam Stats: {len(result['team_stats'])} teams")
        print(f"Player Stats: {len(result['player_stats'])} players")

        # Show some player stats
        if result['player_stats']:
            print(f"\nSample Player (first):")
            player = result['player_stats'][0]
            print(f"  - Name: {player.get('player_name')}")
            print(f"  - Team ID: {player.get('team_id')}")
            print(f"  - Points: {player.get('tot_score')}")
            print(f"  - Rebounds: {player.get('treb_cn')}")
            print(f"  - Assists: {player.get('assist_cn')}")

        return True
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("Sports MCP Tools Test (Direct Handler Calls)")
    print("="*60)

    # Test 1: get_games_by_sport
    test1_passed = test_get_games_by_sport()

    # Test 2: get_game_details
    test2_passed = test_get_game_details()

    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    print(f"get_games_by_sport: {'✅ PASS' if test1_passed else '❌ FAIL'}")
    print(f"get_game_details:   {'✅ PASS' if test2_passed else '❌ FAIL'}")
    print("="*60)

    if test1_passed and test2_passed:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
