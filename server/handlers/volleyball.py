"""배구 전용 핸들러 함수."""
from typing import Any, Dict

from server.handlers._common import safe_int, safe_float


def _build_volleyball_player_data(player: Dict[str, Any]) -> Dict[str, Any]:
  """배구 선수 개별 데이터 생성.

  volleyballPlayerStat API 필드를 프론트엔드 VolleyballPlayerStats 인터페이스에 맞춤.
  모든 수치는 시즌 누적 평균(경기당/세트당).
  """
  kills = safe_float(player.get("atk_success_cn"), 0.0)
  attacks = safe_float(player.get("atk_try_cn"), 0.0)

  result: Dict[str, Any] = {
    "number": safe_int(player.get("back_no"), 0),
    "name": player.get("player_name", ""),
    "position": "",
    "sets": safe_int(player.get("in_set_cn", player.get("set_cn", 0)), 0),
    "points": safe_float(player.get("tot_score", player.get("run_cn", player.get("score_cn", 0.0))), 0.0),
    "attacks": attacks,
    "kills": kills,
    "blocks": safe_float(player.get("block_success_cn"), 0.0),
    "aces": safe_float(player.get("srv_success_cn"), 0.0),
    "digs": safe_float(player.get("dig_success_cn"), 0.0),
    "minutes": 0,  # 정렬 키 (배구 미적용)
  }
  # attackPct: attacks > 0일 때만 키 포함 (없으면 키 생략 → JS undefined → Zod optional 통과)
  if attacks > 0:
    result["attackPct"] = f"{round(kills / attacks * 100, 1)}%"

  return result
