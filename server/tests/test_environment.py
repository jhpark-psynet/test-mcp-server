"""환경 설정 테스트 스크립트.

다양한 ENV 값으로 Config를 테스트합니다.

사용법:
    # Development 환경 테스트 (기본)
    python test_environment.py

    # Production 환경 테스트
    ENV=production python test_environment.py
"""
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def print_section(title: str):
    """Print a section header."""
    print(f"\n{'=' * 80}")
    print(f" {title}")
    print('=' * 80)


def print_info(label: str, value: str):
    """Print info."""
    print(f"  {label:.<40} {value}")


def test_environment():
    """환경 설정 테스트."""
    # 환경 변수 출력
    env = os.getenv('ENV', 'development')
    print_section(f"Testing Environment: {env.upper()}")

    # Config 로드
    from server.config import CONFIG

    # 기본 설정
    print("\n📋 Basic Configuration:")
    print_info("Environment", CONFIG.environment)
    print_info("App Name", CONFIG.app_name)
    print_info("Host:Port", f"{CONFIG.host}:{CONFIG.port}")
    print_info("Log Level", CONFIG.log_level)

    # Sports API 설정
    print("\n🏀 Sports API Configuration:")
    print_info("Base URL", CONFIG.sports_api_base_url)
    print_info("API Key Set", "✓ Yes" if CONFIG.sports_api_key else "✗ No")
    print_info("API Key (masked)",
               CONFIG.sports_api_key[:10] + "..." if CONFIG.sports_api_key else "Not set")
    print_info("Timeout", f"{CONFIG.sports_api_timeout_s}s")
    print_info("Use Mock Data", str(CONFIG.use_mock_sports_data))
    print_info("Has Sports API", "✓ Yes" if CONFIG.has_sports_api else "✗ No")
    print_info("Use Real API", "✓ Yes" if CONFIG.use_real_sports_api else "✗ No")

    # 환경별 예상 설정 검증
    print("\n✅ Environment Validation:")

    if CONFIG.environment == "development":
        checks = [
            ("Log Level", CONFIG.log_level == "DEBUG", "Should be DEBUG"),
            ("Mock Data", CONFIG.use_mock_sports_data == True, "Should be True"),
            ("Real API", CONFIG.use_real_sports_api == False, "Should be False"),
        ]
    elif CONFIG.environment == "production":
        checks = [
            ("Log Level", CONFIG.log_level == "INFO", "Should be INFO"),
            ("Mock Data", CONFIG.use_mock_sports_data == False, "Should be False"),
            ("API Key", bool(CONFIG.sports_api_key and CONFIG.sports_api_key != "dummy_for_development"),
             "Should have real API key"),
        ]
    else:
        checks = []
        print(f"⚠️  Unknown environment: {CONFIG.environment}")

    for check_name, result, description in checks:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {check_name} - {description}")

    # 전체 결과
    all_passed = all(result for _, result, _ in checks)

    print("\n" + "=" * 80)
    if all_passed:
        print(f"✅ All checks passed for {CONFIG.environment} environment!")
        return 0
    else:
        print(f"❌ Some checks failed for {CONFIG.environment} environment!")
        return 1


if __name__ == "__main__":
    sys.exit(test_environment())
