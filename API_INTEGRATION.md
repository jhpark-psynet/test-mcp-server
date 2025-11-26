# Sports API Integration Guide

이 문서는 실제 Sports API를 통합하기 위한 설정 가이드입니다.
아래 정보를 채워주세요.

## API 기본 정보

**Base URL**: `http://data.psynet.co.kr:10005/data3V1/livescore`

**인증 방식**: Query Parameter (api_key)

**API Key**: `.env` 파일에 설정하세요

```bash
SPORTS_API_KEY=your_actual_api_key_here
```

## API 엔드포인트 명세

아래 각 기능별로 **실제 API 경로**, **파라미터**, **응답 예시**를 채워주세요.

---

### 1. 경기 목록 조회 (Get Games by Sport)

**기능**: 특정 날짜의 스포츠 경기 목록을 조회합니다.

**엔드포인트**:
```
TODO: 실제 경로를 입력하세요
예: GET /games
또는: GET /livescore (파라미터로 구분)
```

**요청 파라미터**:
```
TODO: 필요한 파라미터를 입력하세요
예:
- date: YYYYMMDD (예: 20251118)
- sport: basketball, baseball, football
- api_key: YOUR_API_KEY
```

**전체 URL 예시**:
```
TODO: 실제 호출 URL 예시
예: http://data.psynet.co.kr:10005/data3V1/livescore?date=20251118&sport=basketball&api_key=xxx
```

**응답 예시 (JSON)**:
```json
TODO: 실제 API 응답 예시를 붙여넣으세요
{
  "games": [
    {
      "game_id": "...",
      "league_name": "...",
      "home_team_name": "...",
      "away_team_name": "...",
      "home_score": 0,
      "away_score": 0,
      "match_date": "...",
      "match_time": "...",
      "state": "f or b",
      ...
    }
  ]
}
```

**필드 매핑**:
```
TODO: API 응답 필드 → 내부 필드 매핑
예:
API 필드명         →  내부 필드명
--------------       ------------
gameId           →  game_id
leagueName       →  league_name
homeTeamName     →  home_team_name
...
```

---

### 2. 경기 상세 조회 (Get Game Details)

**기능**: 특정 경기의 상세 정보 (팀 통계 + 선수 통계)를 조회합니다.

**엔드포인트**:
```
TODO: 실제 경로를 입력하세요
예: GET /game_details
```

**요청 파라미터**:
```
TODO: 필요한 파라미터를 입력하세요
예:
- game_id: OT2025313104229
- api_key: YOUR_API_KEY
```

**전체 URL 예시**:
```
TODO: 실제 호출 URL 예시
```

**응답 예시 (JSON)**:
```json
TODO: 실제 API 응답 예시를 붙여넣으세요
{
  "game_info": {...},
  "team_stats": [...],
  "player_stats": [...]
}
```

**필드 매핑**:
```
TODO: API 응답 필드 → 내부 필드 매핑
```

---

### 3. 팀 통계 조회 (Get Team Stats)

**기능**: 특정 경기의 팀별 통계를 조회합니다.

**엔드포인트**:
```
TODO: 실제 경로를 입력하세요
예: GET /team_stats
또는 경기 상세 조회와 동일한 경우 "동일" 표기
```

**요청 파라미터**:
```
TODO: 필요한 파라미터를 입력하세요
```

**전체 URL 예시**:
```
TODO: 실제 호출 URL 예시
```

**응답 예시 (JSON)**:
```json
TODO: 실제 API 응답 예시
[
  {
    "home_team_name": "...",
    "home_team_fgm_cn": "45",
    "home_team_fga_cn": "88",
    ...
  },
  {
    "away_team_name": "...",
    ...
  }
]
```

**필드 매핑**:
```
TODO: API 응답 필드 → 내부 필드 매핑
```

---

### 4. 선수 통계 조회 (Get Player Stats)

**기능**: 특정 경기의 선수별 통계를 조회합니다.

**엔드포인트**:
```
TODO: 실제 경로를 입력하세요
예: GET /player_stats
또는 경기 상세 조회와 동일한 경우 "동일" 표기
```

**요청 파라미터**:
```
TODO: 필요한 파라미터를 입력하세요
```

**전체 URL 예시**:
```
TODO: 실제 호출 URL 예시
```

**응답 예시 (JSON)**:
```json
TODO: 실제 API 응답 예시
[
  {
    "player_name": "...",
    "team_id": "...",
    "tot_score": 28,
    "treb_cn": "5",
    "assist_cn": "6",
    ...
  }
]
```

**필드 매핑**:
```
TODO: API 응답 필드 → 내부 필드 매핑
```

---

## 에러 응답

**에러 발생 시 응답 형식**:
```json
TODO: 에러 응답 예시를 입력하세요
{
  "error": "...",
  "message": "..."
}
```

---

## 테스트 방법

문서를 작성한 후, 다음 명령으로 API를 테스트할 수 있습니다:

```bash
# 1. .env 파일에 API Key 설정
echo "SPORTS_API_KEY=your_key_here" >> .env

# 2. 테스트 스크립트 실행
.venv/bin/python test_sports_api_integration.py
```

---

## 참고 사항

1. **날짜 형식**: YYYYMMDD (예: 20251118)
2. **스포츠 종목**: basketball, baseball, football 등
3. **경기 상태**:
   - `f`: Finished (종료)
   - `b`: Before (예정)
   - `진행중`: In Progress
4. **타임아웃**: 기본 10초 (SPORTS_API_TIMEOUT_S로 조정 가능)

---

## 작성 완료 후

이 문서를 작성하면, 코드가 자동으로 실제 API를 호출하도록 업데이트됩니다.
작성이 완료되면 다시 알려주세요!
