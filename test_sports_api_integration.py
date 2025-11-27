"""Sports API 통합 테스트 스크립트.

이 스크립트는 실제 Sports API를 호출하고 응답을 검증합니다.
API_INTEGRATION.md 문서를 작성한 후 실행하세요.

사용법:
    # Mock 데이터로 테스트 (기본)
    python test_sports_api_integration.py

    # 실제 API로 테스트
    USE_MOCK_SPORTS_DATA=false SPORTS_API_KEY=your_key python test_sports_api_integration.py
"""
import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from server.services.sports import SportsClientFactory
from server.config import CONFIG


def print_section(title: str):
    """Print a section header."""
    print(f"\n{'=' * 80}")
    print(f" {title}")
    print('=' * 80)


def print_success(message: str):
    """Print success message."""
    print(f"✅ {message}")


def print_error(message: str):
    """Print error message."""
    print(f"❌ {message}")


def print_info(message: str):
    """Print info message."""
    print(f"ℹ️  {message}")


def test_configuration():
    """테스트 1: 설정 확인."""
    print_section("Test 1: Configuration Check")

    print_info(f"Base URL: {CONFIG.sports_api_base_url}")
    print_info(f"API Key: {'✓ Set' if CONFIG.sports_api_key else '✗ Not set'}")
    print_info(f"Timeout: {CONFIG.sports_api_timeout_s}s")
    print_info(f"Use Mock Data: {CONFIG.use_mock_sports_data}")

    if CONFIG.use_real_sports_api:
        print_success("Real API mode enabled")
        if not CONFIG.sports_api_key:
            print_error("API Key is required for real API calls!")
            return False
    else:
        print_success("Mock data mode enabled")

    return True


def test_games_by_sport():
    """테스트 2: 경기 목록 조회."""
    print_section("Test 2: Get Games by Sport")

    test_date = "20251125"
    test_sport = "basketball"
    client = SportsClientFactory.create_client(test_sport)

    try:
        print_info(f"Fetching games for {test_sport} on {test_date}...")
        games = client.get_games_by_sport(test_date)

        print_success(f"Retrieved {len(games)} games")

        if games:
            # Show first game details
            first_game = games[0]
            print("\nFirst game details:")
            print(json.dumps(first_game, indent=2, ensure_ascii=False))

            # Validate required fields
            required_fields = ["game_id", "home_team_name", "away_team_name", "state"]
            missing_fields = [f for f in required_fields if f not in first_game]

            if missing_fields:
                print_error(f"Missing required fields: {missing_fields}")
                print_error("You may need to update API_INTEGRATION.md field mappings")
                return False
            else:
                print_success("All required fields present")

        return True

    except Exception as e:
        print_error(f"Failed to fetch games: {e}")
        print_info("Check your API_INTEGRATION.md configuration")
        return False


def test_team_stats():
    """테스트 3: 팀 통계 조회."""
    print_section("Test 3: Get Team Stats")

    test_game_id = "OT2025313104280"  # NBA: 인디애나 vs 디트로이트
    client = SportsClientFactory.create_client('basketball')

    try:
        print_info(f"Fetching team stats for game {test_game_id}...")
        stats = client.get_team_stats(test_game_id)

        if stats and len(stats) >= 2:
            print_success(f"Retrieved team stats for 2 teams")

            print("\nHome team stats:")
            print(json.dumps(stats[0], indent=2, ensure_ascii=False))

            # Validate required fields
            required_fields = ["home_team_id", "home_team_fgm_cn", "home_team_fga_cn"]
            missing_fields = [f for f in required_fields if f not in stats[0]]

            if missing_fields:
                print_error(f"Missing required fields: {missing_fields}")
                return False
            else:
                print_success("All required fields present")

            return True
        else:
            print_error("Expected 2 team stats (home and away)")
            return False

    except Exception as e:
        print_error(f"Failed to fetch team stats: {e}")
        return False


def test_player_stats():
    """테스트 4: 선수 통계 조회."""
    print_section("Test 4: Get Player Stats")

    test_game_id = "OT2025313104280"  # NBA: 인디애나 vs 디트로이트
    client = SportsClientFactory.create_client('basketball')

    try:
        print_info(f"Fetching player stats for game {test_game_id}...")
        stats = client.get_player_stats(test_game_id)

        if stats and len(stats) > 0:
            print_success(f"Retrieved player stats for {len(stats)} players")

            print("\nFirst player stats:")
            print(json.dumps(stats[0], indent=2, ensure_ascii=False))

            # Validate required fields
            required_fields = ["player_name", "team_id", "tot_score", "treb_cn", "assist_cn"]
            missing_fields = [f for f in required_fields if f not in stats[0]]

            if missing_fields:
                print_error(f"Missing required fields: {missing_fields}")
                return False
            else:
                print_success("All required fields present")

            return True
        else:
            print_error("No player stats returned")
            return False

    except Exception as e:
        print_error(f"Failed to fetch player stats: {e}")
        return False


def test_error_handling():
    """테스트 5: 에러 처리."""
    print_section("Test 5: Error Handling")

    # Test invalid date format
    try:
        print_info("Testing invalid date format...")
        client = SportsClientFactory.create_client('basketball')
        client.get_games_by_sport("invalid")
        print_error("Should have raised ValueError for invalid date")
        return False
    except (ValueError, Exception) as e:
        print_success(f"Correctly raised error: {e}")

    # Test invalid sport
    try:
        print_info("Testing invalid sport...")
        client = SportsClientFactory.create_client("invalid")
        print_error("Should have raised ValueError for invalid sport")
        return False
    except ValueError as e:
        print_success(f"Correctly raised ValueError: {e}")

    # Test non-existent game
    try:
        print_info("Testing non-existent game...")
        client = SportsClientFactory.create_client('basketball')
        client.get_team_stats("NONEXISTENT")
        print_error("Should have raised ValueError for non-existent game")
        return False
    except (ValueError, Exception) as e:
        print_success(f"Correctly raised error: {e}")

    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print(" Sports API Integration Test Suite")
    print("=" * 80)

    results = []

    # Run tests
    results.append(("Configuration", test_configuration()))
    results.append(("Get Games by Sport", test_games_by_sport()))
    results.append(("Get Team Stats", test_team_stats()))
    results.append(("Get Player Stats", test_player_stats()))
    results.append(("Error Handling", test_error_handling()))

    # Print summary
    print_section("Test Summary")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print_success("All tests passed!")
        print_info("Your Sports API integration is working correctly")

        if CONFIG.use_mock_sports_data:
            print("\nNext steps:")
            print("1. Complete API_INTEGRATION.md with real API details")
            print("2. Set SPORTS_API_KEY in your .env file")
            print("3. Run tests with: USE_MOCK_SPORTS_DATA=false python test_sports_api_integration.py")
        else:
            print_success("Real API integration is working!")

        return 0
    else:
        print_error("Some tests failed")
        print_info("Please check the error messages above and update your configuration")
        return 1


if __name__ == "__main__":
    sys.exit(main())
