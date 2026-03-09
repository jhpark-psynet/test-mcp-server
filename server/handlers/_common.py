"""공통 유틸리티 함수 및 상수."""
from typing import Any, List, Union

# Team logo URL template
TEAM_LOGO_URL_TEMPLATE = "https://lscdn.psynet.co.kr/livescore/photo/spt/livescore/emb_new/emblem_mid_{team_id}.png"


def get_team_logo_url(team_id: str) -> str:
  """팀 로고 URL 생성."""
  if not team_id:
    return ""
  return TEAM_LOGO_URL_TEMPLATE.format(team_id=team_id)


def build_recent_games(wins: int, losses: int) -> List[str]:
  """최근 5경기 결과 배열 생성 (승리 먼저, 패배 나중)."""
  total = wins + losses
  if total == 0:
    return []
  return ['W'] * wins + ['L'] * losses


def safe_int(value: Union[str, int, float, None], default: int = 0) -> int:
  """안전하게 int로 변환."""
  if value is None:
    return default
  if isinstance(value, int):
    return value
  if isinstance(value, float):
    return int(value)
  if isinstance(value, str):
    value = value.strip()
    if not value:
      return default
    try:
      return int(value)
    except ValueError:
      return default
  return default


def safe_float(value: Any, default: float = 0.0) -> float:
  """안전하게 float로 변환."""
  if value is None:
    return default
  try:
    return float(value)
  except (ValueError, TypeError):
    return default


def _calc_percentage(numerator: Any, denominator: Any) -> str:
  """백분율 계산 (문자열 반환).

  Args:
    numerator: 분자
    denominator: 분모

  Returns:
    백분율 문자열 (예: "75.0%") 또는 "-"
  """
  num = safe_int(numerator, 0)
  denom = safe_int(denominator, 0)
  if denom == 0:
    return "-"
  return f"{round(num / denom * 100, 1)}%"
