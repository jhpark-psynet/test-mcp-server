"""Test sports MCP tools."""
import sys
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from server.handlers import get_games_by_sport_handler, get_game_details_handler


@pytest.mark.asyncio
async def test_get_games_by_sport():
    """Test get_games_by_sport handler."""
    print("\n" + "="*60)
    print("Testing get_games_by_sport")
    print("="*60)

    arguments = {
        "date": "20251118",
        "sport": "basketball"
    }

    try:
        result = await get_games_by_sport_handler(arguments)
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


@pytest.mark.asyncio
async def test_get_game_details():
    """Test get_game_details handler."""
    print("\n" + "="*60)
    print("Testing get_game_details")
    print("="*60)

    arguments = {
        "game_id": "OT2025313104237"
    }

    try:
        result = await get_game_details_handler(arguments)
        print(f"\n✅ Success!")
        print(f"\nResult type: {type(result)}")
        print(f"\nResult keys: {list(result.keys())}")
        print(f"\nLeague: {result.get('league')}")
        print(f"Date: {result.get('date')}")
        print(f"Status: {result.get('status')}")

        # Check team data
        home_team = result.get('homeTeam', {})
        away_team = result.get('awayTeam', {})
        print(f"\nHome Team: {home_team.get('name')} - Score: {home_team.get('score')}")
        print(f"Away Team: {away_team.get('name')} - Score: {away_team.get('score')}")
        print(f"Home Players: {len(home_team.get('players', []))}")
        print(f"Away Players: {len(away_team.get('players', []))}")

        # Check game records
        game_records = result.get('gameRecords', [])
        print(f"\nGame Records: {len(game_records)} stats")
        if game_records:
            print(f"Sample record: {game_records[0]}")

        return True
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("Sports MCP Tools Test (Direct Handler Calls)")
    print("="*60)

    # Test 1: get_games_by_sport
    test1_passed = await test_get_games_by_sport()

    # Test 2: get_game_details
    test2_passed = await test_get_game_details()

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
    import asyncio
    asyncio.run(main())
