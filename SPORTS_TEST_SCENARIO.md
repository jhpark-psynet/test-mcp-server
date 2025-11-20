# Sports MCP Tools - Test Scenario

## Overview
스포츠 데이터 조회를 위한 MCP 도구 테스트 시나리오

## Tool Architecture

### Tool 1: `get_games_by_sport` (Text-based)
- **목적**: 특정 날짜의 스포츠 경기 목록 조회
- **입력**:
  - `date`: YYYYMMDD 형식 (예: "20251118")
  - `sport`: 스포츠 종목 ("basketball", "baseball", "football")
- **출력**: 텍스트 형식의 경기 목록 (경기 ID 포함)

### Tool 2: `get_game_details` (Widget-based)
- **목적**: 특정 경기의 상세 정보 (팀 통계 + 선수 통계) 조회 및 시각화
- **입력**:
  - `game_id`: 경기 ID (Tool 1에서 얻은 game_id)
- **출력**: React 컴포넌트 (팀 통계 + 선수 통계를 시각적으로 표현)
- **내부 동작**:
  1. `SportsApiClient.get_team_stats(game_id)` 호출
  2. `SportsApiClient.get_player_stats(game_id)` 호출
  3. 두 데이터를 조합하여 React 컴포넌트 생성

## User Interaction Flow

### Scenario 1: 오늘 클리브랜드 경기 결과 조회

#### Step 1: 사용자 질문
```
사용자: "오늘 클리브랜드 경기 결과 알려줘"
```

#### Step 2: LLM 분석 및 첫 번째 도구 호출
- LLM이 질문을 분석:
  - 날짜: "오늘" → `20251118` (시스템 날짜 기준)
  - 팀: "클리브랜드"
  - 스포츠: "basketball" (컨텍스트로부터 추론 또는 기본값)

- **Tool Call 1**: `get_games_by_sport`
  ```json
  {
    "date": "20251118",
    "sport": "basketball"
  }
  ```

#### Step 3: MCP 서버 응답
```markdown
## Basketball Games on 20251118

### [NBA]
- **클리블랜드** 118 - 106 **밀워키** (Finished, W)
  - Arena: 로킷 모기지 필드하우스
  - Game ID: `OT2025313104229`

- **올랜도** 105 - 87 **샌안토니오** (Finished, W)
  - Arena: 아멕스 센터
  - Game ID: `OT2025313104237`

### [KBL]
- **대구가스공사** 93 - 94 **부산KCC** (09:00, Scheduled)
  - Arena: 대구실내체육관
  - Game ID: `KBL2025118001`
```

#### Step 4: LLM이 결과 분석 및 두 번째 도구 호출
- LLM이 "클리브랜드" 경기를 찾음: `OT2025313104229`
- **Tool Call 2**: `get_game_details`
  ```json
  {
    "game_id": "OT2025313104229"
  }
  ```

#### Step 5: MCP 서버가 React 컴포넌트 반환
- 내부적으로 API 호출:
  1. `get_team_stats("OT2025313104229")`
  2. `get_player_stats("OT2025313104229")`
- 두 데이터를 조합하여 `GameStatsWidget` 컴포넌트 생성
- 컴포넌트에 팀 통계 테이블, 선수 통계 테이블, 경기 요약 포함

#### Step 6: 사용자에게 시각화된 결과 표시
- 리액트 컴포넌트가 렌더링되어 사용자에게 표시됨
- 팀별 슈팅%, 리바운드, 어시스트 등 시각적으로 비교
- 주요 선수들의 득점, 리바운드, 어시스트 통계 표시

---

### Scenario 2: 어제 NBA 경기 중 특정 경기 상세 조회

#### Step 1: 사용자 질문
```
사용자: "어제 NBA 경기 중에서 올랜도 경기 상세히 보여줘"
```

#### Step 2: LLM 분석 및 첫 번째 도구 호출
- 날짜: "어제" → `20251117`
- 스포츠: "basketball" (NBA)

- **Tool Call 1**: `get_games_by_sport`
  ```json
  {
    "date": "20251117",
    "sport": "basketball"
  }
  ```

#### Step 3: MCP 서버 응답 (경기 목록)
- 해당 날짜의 NBA 경기 목록 반환
- LLM이 "올랜도" 팀이 포함된 경기의 game_id 식별

#### Step 4: LLM이 두 번째 도구 호출
- **Tool Call 2**: `get_game_details`
  ```json
  {
    "game_id": "OT2025313104237"
  }
  ```

#### Step 5: React 컴포넌트 반환 및 표시
- 팀 통계 + 선수 통계가 포함된 위젯 표시

---

### Scenario 3: 특정 날짜의 KBL 경기 조회

#### Step 1: 사용자 질문
```
사용자: "2025년 1월 18일 KBL 경기 결과 보여줘"
```

#### Step 2: LLM 분석 및 도구 호출
- 날짜: `20250118`
- 스포츠: "basketball"

- **Tool Call 1**: `get_games_by_sport`

#### Step 3: 경기 목록 확인
- KBL 경기 목록 표시
- 사용자가 특정 경기에 대해 추가 질문 가능

#### Step 4 (Optional): 상세 조회
```
사용자: "첫 번째 경기 자세히 보여줘"
```
- LLM이 `get_game_details` 호출

---

## Test Cases

### Test Case 1: 경기 목록 조회 - 성공
- **Input**: `{"date": "20251118", "sport": "basketball"}`
- **Expected**: 3개의 농구 경기 목록 (NBA 2개, KBL 1개)
- **Verify**: 각 경기에 game_id, 팀 이름, 점수/시간, 경기장 정보 포함

### Test Case 2: 경기 목록 조회 - 빈 결과
- **Input**: `{"date": "20251119", "sport": "basketball"}`
- **Expected**: "No basketball games found on 20251119"
- **Verify**: 오류 없이 빈 결과 메시지 반환

### Test Case 3: 경기 목록 조회 - 잘못된 날짜 형식
- **Input**: `{"date": "2025-11-18", "sport": "basketball"}`
- **Expected**: ValueError with message about invalid date format
- **Verify**: `isError: true` 설정됨

### Test Case 4: 경기 목록 조회 - 잘못된 스포츠 종목
- **Input**: `{"date": "20251118", "sport": "soccer"}`
- **Expected**: ValueError with message about invalid sport
- **Verify**: `isError: true` 설정됨

### Test Case 5: 경기 상세 조회 - 성공 (종료된 경기)
- **Input**: `{"game_id": "OT2025313104229"}`
- **Expected**: React 컴포넌트 (팀 통계 + 선수 통계 포함)
- **Verify**:
  - 컴포넌트에 양 팀의 슈팅%, 리바운드, 어시스트 등 포함
  - 각 팀의 선수 통계 (득점, 리바운드, 어시스트, 슈팅% 등) 포함

### Test Case 6: 경기 상세 조회 - 실패 (시작 전 경기)
- **Input**: `{"game_id": "KBL2025118001"}` (state: "b")
- **Expected**: ValueError with message "Game has not started yet"
- **Verify**: `isError: true` 설정됨

### Test Case 7: 경기 상세 조회 - 실패 (존재하지 않는 경기)
- **Input**: `{"game_id": "INVALID_GAME_ID"}`
- **Expected**: ValueError with message "Game INVALID_GAME_ID not found"
- **Verify**: `isError: true` 설정됨

### Test Case 8: 통합 시나리오 (경기 목록 → 상세 조회)
- **Step 1**: `get_games_by_sport("20251118", "basketball")`
- **Verify**: 경기 목록 반환
- **Step 2**: 목록에서 game_id 추출 (예: "OT2025313104229")
- **Step 3**: `get_game_details("OT2025313104229")`
- **Verify**: 해당 경기의 상세 통계 컴포넌트 반환

---

## Expected Data Flow

```
User Question
    ↓
LLM Analysis (날짜, 스포츠 추출)
    ↓
Tool 1: get_games_by_sport(date, sport)
    ↓
MCP Server → SportsApiClient.get_games_by_sport()
    ↓
Text Response (경기 목록 with game_ids)
    ↓
LLM 분석 (원하는 경기의 game_id 식별)
    ↓
Tool 2: get_game_details(game_id)
    ↓
MCP Server → SportsApiClient.get_team_stats(game_id)
             SportsApiClient.get_player_stats(game_id)
    ↓
React Component (팀 통계 + 선수 통계 시각화)
    ↓
User sees visual widget
```

---

## Implementation Notes

### Current Status
- ✅ Tool 1: `get_games_by_sport` 구현됨 (텍스트 기반)
- ❌ Tool 2: `get_game_details` 구현 필요 (위젯 기반)
- ✅ API Client: `SportsApiClient` 구현됨
- ✅ Mock Data: 경기, 팀 통계, 선수 통계 데이터 준비됨

### Next Steps
1. Tool 2 (`get_game_details`) 구현:
   - Widget-based tool로 등록
   - React 컴포넌트 생성 로직 추가
   - 팀 통계 + 선수 통계를 하나의 컴포넌트로 조합
2. 기존 `get_team_stats`, `get_player_stats` 도구 제거
3. 통합 테스트 실행
