# test-mcp-server

## 1. Project Overview

### 목적
FastMCP 2.0과 OpenAI Apps SDK를 활용하여 React 컴포넌트를 MCP 클라이언트(ChatGPT)에게 리소스로 전달하는 MCP 서버 구축.

### 주요 기능
- **React 위젯 제공**: React로 만든 UI 컴포넌트를 HTML로 빌드하여 MCP 리소스로 노출
- **동적 Props 전달**: `structuredContent`를 통해 React 컴포넌트에 props 전달
- **Hot Reload**: 서버 코드 변경 시 자동 재시작

### 핵심 가치
ChatGPT가 렌더링할 수 있는 인터랙티브 UI 위젯을 Python MCP 서버로 제공하여, 대화형 AI 경험을 확장.

### 아키텍처 흐름
```
React (TSX) → Vite Build → HTML/JS/CSS → MCP Server → ChatGPT Client
                                           ↓
                                    structuredContent (props)
```

## 2. Technology Stack

### Backend (Python)
- **FastMCP 2.0**: MCP 서버 프레임워크
- **Uvicorn**: ASGI 서버 (hot reload 지원)
- **Starlette**: ASGI 웹 프레임워크 (CORS 미들웨어)
- **Pydantic**: 데이터 검증 및 직렬화

### Frontend (React)
- **React 19**: UI 라이브러리
- **TypeScript**: 타입 안전성
- **Tailwind CSS 4.1**: 유틸리티 CSS 프레임워크
- **Vite 7**: 빌드 도구 (빠른 HMR, ES2022 타겟)

### Build & Tools
- **tsx**: TypeScript 실행 환경
- **fast-glob**: 파일 패턴 매칭
- **npm**: 패키지 관리 (루트 스크립트)
- **uv**: Python 패키지 관리 (빠른 pip)

## 3. Available Widgets

서버에 포함된 빌트인 위젯 2개:

### 1. Example Widget (`example`)
- **목적**: 기본 위젯 기능 데모
- **Props**: `message` (string)
- **위치**: `components/src/example/`
- **사용법**: React 위젯과 props 전달 방식 학습용
- **상태**: 테스트용으로 코드만 유지 (툴 목록에서 제외)

### 2. Game Result Viewer (`game-result-viewer`)
- **목적**: 스포츠 경기 상세 통계 시각화
- **Props**: `GameData` (league, date, status, homeTeam, awayTeam, gameRecords)
- **위치**: `components/src/game-result-viewer/`
- **기능**:
  - 경기 정보 헤더 (리그, 날짜, 상태)
  - 팀별 스코어 및 기록
  - 선수별 상세 통계 (득점, 리바운드, 어시스트 등)
  - 팀 통계 비교 (필드골, 3점슛, 자유투 등)
  - Zod 스키마 검증
  - 로딩 상태 처리 (window.openai.toolOutput 폴링)
- **사용 툴**: `get_game_details`

## 4. Available Tools

서버가 제공하는 MCP 도구 2개:

### 1. Get Games by Sport (텍스트 도구)
- **이름**: `get_games_by_sport`
- **타입**: Text-based tool
- **입력**:
  - `date` (string) - 경기 날짜 (YYYYMMDD 형식)
  - `sport` (string) - 스포츠 종류 (basketball, soccer, volleyball, football)
  - `force_refresh` (boolean, optional) - 캐시 무시하고 새로 조회
- **출력**: 경기 일정 및 결과 (팀명, 스코어, 시간, 경기장, 경기 상태)
- **기능**:
  - 특정 날짜의 경기 목록 조회
  - 팀명 필터링 가능 (home_team_name, away_team_name 검색)
  - 일반적인 팀 별칭 지원 (Warriors, Cavs, Thunder 등)
  - **TTL 캐시**: 5분간 결과 캐싱으로 API 호출 감소
- **예시**:
  - `{"date": "20251118", "sport": "basketball"}` → NBA/KBL/WKBL 경기 목록

### 2. Get Game Details (위젯 도구)
- **이름**: `get_game_details`
- **타입**: Widget-based tool
- **입력**: `game_id` (string) - 경기 고유 ID
- **출력**: 인터랙티브 경기 상세 통계 위젯
- **위젯**: Game Result Viewer 컴포넌트 사용
- **기능**:
  - 팀 통계 (필드골, 3점슛, 자유투, 리바운드 등)
  - 선수별 상세 통계 (득점, 리바운드, 어시스트, 슈팅 성공률 등)
  - 인터랙티브 UI로 데이터 시각화
- **지원 상태**:
  - 경기 전 (state='s'): 팀 비교, 상대전적, 순위
  - 경기 중 (state='p'): 실시간 스코어, 현재 통계
  - 경기 후 (state='f'): 최종 스코어, 전체 선수 통계
- **사용법**: `get_games_by_sport`로 먼저 game_id 확인 후 사용

## 5. Folder Structure (Phase 8 Complete)

```
test-mcp-server/
├── .venv/                          # Python 가상환경
├── .env.development                # 개발 환경 설정
├── .env.production                 # 프로덕션 환경 설정
├── server/                         # Python MCP 서버 (Modularized!)
│   ├── main.py                    # 엔트리포인트 (32줄)
│   ├── config.py                  # 설정 관리 (Pydantic BaseSettings)
│   ├── errors.py                  # 에러 정의
│   ├── logging_config.py          # 로깅 설정
│   │
│   ├── models/                    # 도메인 모델
│   │   ├── __init__.py
│   │   ├── widget.py             # Widget dataclass
│   │   ├── tool.py               # ToolDefinition (has_widget property)
│   │   └── schemas.py            # Pydantic 스키마
│   │
│   ├── services/                  # 비즈니스 로직
│   │   ├── __init__.py
│   │   ├── asset_loader.py       # HTML 자산 로딩
│   │   ├── cache.py              # TTL 캐시 (Phase 7)
│   │   ├── widget_registry.py    # 위젯 빌드
│   │   ├── tool_registry.py      # 툴 빌드 및 인덱싱
│   │   │
│   │   └── sports/               # 스포츠 API (모듈화, Phase 6)
│   │       ├── __init__.py       # SportsClientFactory
│   │       ├── base/             # 공통 기반 클래스
│   │       │   ├── __init__.py
│   │       │   ├── client.py    # BaseSportsClient (HTTP 로직)
│   │       │   ├── endpoints.py # 공통 엔드포인트 설정
│   │       │   └── mapper.py    # BaseResponseMapper (필드 매핑)
│   │       ├── basketball/       # 농구 전용 모듈
│   │       │   ├── __init__.py
│   │       │   ├── client.py    # BasketballClient
│   │       │   ├── endpoints.py # 농구 API 엔드포인트
│   │       │   ├── mapper.py    # BasketballMapper
│   │       │   └── mock_data.py # 농구 Mock 데이터
│   │       ├── soccer/           # 축구 전용 모듈
│   │       │   ├── __init__.py
│   │       │   ├── client.py    # SoccerClient
│   │       │   ├── endpoints.py # 축구 API 엔드포인트
│   │       │   ├── mapper.py    # SoccerMapper
│   │       │   └── mock_data.py # 축구 Mock 데이터
│   │       ├── volleyball/       # 배구 전용 모듈
│   │       │   ├── __init__.py
│   │       │   ├── client.py    # VolleyballClient
│   │       │   ├── endpoints.py # 배구 API 엔드포인트
│   │       │   ├── mapper.py    # VolleyballMapper
│   │       │   └── mock_data.py # 배구 Mock 데이터
│   │       └── football/         # 미식축구 전용 모듈
│   │           ├── __init__.py
│   │           ├── client.py    # FootballClient
│   │           ├── endpoints.py # 미식축구 API 엔드포인트
│   │           ├── mapper.py    # FootballMapper
│   │           └── mock_data.py # 미식축구 Mock 데이터
│   │
│   ├── handlers/                  # 툴 핸들러
│   │   ├── __init__.py
│   │   └── sports.py             # 스포츠 데이터 핸들러 (factory 패턴 사용)
│   │
│   ├── factory/                   # MCP 서버 팩토리
│   │   ├── __init__.py
│   │   ├── safe_wrapper.py       # SafeFastMCPWrapper (Phase 2)
│   │   ├── server_factory.py     # MCP 서버 생성
│   │   └── metadata_builder.py   # OpenAI 메타데이터
│   │
│   ├── tests/                     # 테스트 스위트
│   │   ├── test_mcp.py           # MCP 통합 테스트
│   │   ├── test_mcp_get_game_details.py  # 게임 상세 테스트
│   │   ├── test_environment.py   # 환경 설정 테스트
│   │   ├── test_sports_api_integration.py  # Sports API 통합 테스트
│   │   ├── test_sports_tools.py  # 스포츠 툴 테스트
│   │   └── unit/                 # 유닛 테스트
│   │       ├── test_endpoints.py
│   │       └── test_client_endpoints.py
│   │
│   └── requirements.txt           # Python 의존성
│
├── components/                     # React 컴포넌트
│   ├── src/                       # React 소스 코드
│   │   ├── index.css              # 글로벌 CSS (Tailwind)
│   │   ├── vite-env.d.ts          # Vite 타입 정의
│   │   ├── example/               # 예제 위젯 (테스트용)
│   │   │   └── index.tsx
│   │   └── game-result-viewer/    # 경기 결과 위젯
│   │       ├── index.tsx          # 메인 컴포넌트
│   │       ├── types.ts           # TypeScript 타입 정의
│   │       └── mock-data.ts       # Mock 데이터
│   │
│   ├── assets/                    # 빌드 결과물 (생성됨)
│   │   ├── example.html           # MCP 서버가 읽는 HTML
│   │   ├── example.js
│   │   ├── example.css
│   │   ├── game-result-viewer.html
│   │   ├── game-result-viewer.js
│   │   ├── game-result-viewer.css
│   │   └── manifest.json          # 빌드 매니페스트
│   │
│   ├── package.json               # Node 의존성
│   ├── tsconfig.json              # TypeScript 설정
│   ├── vite.config.ts             # Vite 설정
│   └── build.ts                   # 빌드 스크립트
│
├── tests/                          # 추가 테스트
│   └── test_cache.py              # 캐시 모듈 테스트 (18개 테스트)
│
├── package.json                    # 루트 빌드 스크립트
├── API_INTEGRATION.md              # API 통합 가이드
├── ARCHITECTURE.md                 # 아키텍처 문서
├── CUSTOMIZATION_GUIDE.md          # 커스터마이징 가이드
├── REFACTORING_PLAN.md            # 리팩토링 계획 (Phase 1-8 ✅)
├── IMPROVEMENT_RECOMMENDATIONS.md  # 개선 제안
├── README.md                       # 사용자 문서
└── claude.md                       # 이 파일 (Claude용)
```

**Phase 1 Refactoring 성과** (2025-11-04):
- ✅ main.py: 933줄 → 32줄 (96.6% 감소)
- ✅ 17개 모듈로 분리 (레이어드 아키텍처)
- ✅ AST 기반 안전한 계산기 (eval() 제거)
- ✅ 통합 테스트: 7/9 통과

**Phase 2 Refactoring 성과** (2025-11-04):
- ✅ SafeFastMCPWrapper 구현 (136줄)
- ✅ FastMCP 비공개 API 안전 접근
- ✅ 초기화 시 내부 API 검증
- ✅ 통합 테스트: 7/9 통과 (기능 유지)

**Phase 3 Refactoring 성과** (2025-11-04):
- ✅ Config 리팩토링: dataclass → Pydantic BaseSettings (44 → 180줄)
- ✅ 환경 변수 자동 검증 (Field validators)
- ✅ .env 파일 자동 로딩
- ✅ 타입 안전성 확보 (포트, 로그 레벨, API URL 검증)
- ✅ 통합 테스트: 7/9 통과 (기능 유지)

**Phase 4 & 5 성과** (2025-11-22):
- ✅ Sports MCP 툴 2개 추가 (get_games_by_sport, get_game_details)
- ✅ Game Result Viewer 위젯 (React 19, Tailwind CSS)
- ✅ 외부 스포츠 API 통합 (팀 통계, 선수 통계)
- ✅ Zod 스키마 검증 및 에러 핸들링
- ✅ 로딩 상태 처리 (window.openai.toolOutput 폴링)

**Phase 6 성과** (2025-11-27):
- ✅ Sports API 모듈화 리팩토링 (스포츠별 분리)
- ✅ Factory 패턴 도입 (SportsClientFactory)
- ✅ 기반 클래스 추상화 (BaseSportsClient, BaseResponseMapper)
- ✅ 스포츠별 독립 모듈 (basketball, soccer, volleyball, football)
- ✅ 폴더 기반 구조로 가독성 및 확장성 향상
- ✅ 통합 테스트: 모든 클라이언트 생성 및 데이터 조회 성공

**Phase 7 성과** (TTL Cache):
- ✅ 인메모리 TTL 캐시 구현 (`server/services/cache.py`)
- ✅ 게임 목록 API 응답 캐싱 (기본 5분)
- ✅ 최대 크기 제한 (기본 100 항목)
- ✅ 데이터 검증 후 캐싱 (필수 필드 체크)
- ✅ `force_refresh` 파라미터로 캐시 우회
- ✅ 캐시 hit/miss 로깅
- ✅ 18개 유닛 테스트 통과

**Phase 8 성과** (Multi-Sport Handler):
- ✅ `get_game_details_handler` 모든 스포츠 지원 리팩토링
- ✅ `BaseSportsClient`에 선택적 메서드 추가 (`get_lineup`, `get_team_rank`, `get_team_vs_list`)
- ✅ `BaseResponseMapper`에 `build_game_records()` 추상 메서드 추가
- ✅ 스포츠별 `gameRecords` 구현 (basketball, soccer, volleyball, football)
- ✅ `has_operation()` 체크로 동적 기능 감지
- ✅ 핸들러 코드 감소: 713 → 624줄
- ✅ 새 스포츠 추가 시 핸들러 수정 불필요

### 파일 역할 요약 (Refactored)

| 파일 | 역할 |
|------|------|
| `server/main.py` | 엔트리포인트 (32줄, 로깅 + 앱 생성) |
| `server/config.py` | Config 클래스 (Pydantic BaseSettings) |
| `server/errors.py` | 에러 정의 |
| `server/logging_config.py` | 구조화된 로깅 설정 |
| `server/models/widget.py` | Widget 도메인 모델 |
| `server/models/tool.py` | ToolDefinition 도메인 모델 |
| `server/models/schemas.py` | Pydantic 스키마 (입력 검증) |
| `server/services/asset_loader.py` | HTML 파일 로딩 (캐싱) |
| `server/services/cache.py` | TTL 캐시 (Phase 7) |
| `server/services/widget_registry.py` | 위젯 빌드 및 인덱싱 |
| `server/services/tool_registry.py` | 툴 빌드 및 인덱싱 |
| `server/services/sports/__init__.py` | SportsClientFactory (Phase 6) |
| `server/services/sports/base/client.py` | BaseSportsClient (공통 HTTP 로직) |
| `server/services/sports/base/endpoints.py` | 공통 엔드포인트 설정 |
| `server/services/sports/base/mapper.py` | BaseResponseMapper (공통 필드 매핑) |
| `server/services/sports/basketball/` | BasketballClient, endpoints, Mapper, Mock 데이터 |
| `server/services/sports/soccer/` | SoccerClient, endpoints, Mapper, Mock 데이터 |
| `server/services/sports/volleyball/` | VolleyballClient, endpoints, Mapper, Mock 데이터 |
| `server/services/sports/football/` | FootballClient, endpoints, Mapper, Mock 데이터 |
| `server/handlers/sports.py` | 스포츠 데이터 핸들러 (factory 패턴) |
| `server/factory/safe_wrapper.py` | SafeFastMCPWrapper (Phase 2) |
| `server/factory/server_factory.py` | MCP 서버 생성 팩토리 |
| `server/factory/metadata_builder.py` | OpenAI 메타데이터 생성 |
| `server/tests/test_mcp.py` | MCP 통합 테스트 |
| `server/tests/test_sports_api_integration.py` | Sports API 통합 테스트 |
| `server/tests/test_environment.py` | 환경 설정 테스트 |
| `tests/test_cache.py` | 캐시 모듈 테스트 (18개 테스트) |
| `components/src/example/` | 예제 위젯 (테스트용) |
| `components/src/game-result-viewer/` | 경기 결과 위젯 (스포츠 통계) |
| `components/build.ts` | Vite 빌드 (HTML 생성) |
| `components/assets/*.html` | MCP 리소스로 전달 |

## 6. Development Guidelines

### 아키텍처 패턴

#### 팩토리 함수 (Factory Pattern)
서버는 테스트 용이성을 위해 팩토리 함수로 구성됩니다:

```python
def create_mcp_server(cfg: Config) -> FastMCP:
    """FastMCP 서버를 생성하고 핸들러를 등록."""
    # 의존성 주입 가능 → 테스트 시 Mock Config 사용 가능

def create_app(cfg: Config):
    """ASGI 앱 생성 (CORS 포함)."""
    # 프로덕션/테스트 환경 분리 가능
```

#### 레이어드 아키텍처
`server/main.py`는 명확한 섹션으로 분리:
1. **Configuration** - 환경 변수 기반 설정
2. **Logging** - 구조화된 로깅
3. **Domain models** - Widget, ToolInput
4. **Assets loading** - HTML 로딩 로직
5. **Widget registry** - 위젯 빌드/인덱싱
6. **Metadata helpers** - OpenAI 메타데이터
7. **MCP server** - 핸들러 등록
8. **App factory** - ASGI 앱 생성

### 코딩 규칙

#### Python (server/)
- **스타일**: PEP 8 준수
- **타입 힌팅**: 모든 함수에 타입 힌트 필수
- **Docstring**: 모듈 레벨 + 공개 함수에 설명 필수
- **비동기**: MCP 핸들러는 `async def` 사용
- **Immutability**: Config는 `frozen=True` dataclass

```python
@dataclass(frozen=True)
class Config:
    """런타임/빌드 구성값 모음."""
    app_name: str = "test-mcp-server"
    host: str = os.getenv("HTTP_HOST", "0.0.0.0")

async def _call_tool_request(req: types.CallToolRequest) -> types.ServerResult:
    """Handle tool call requests."""
    logger.warning("Unknown tool call: %s", req.params.name)
    # ...
```

#### TypeScript (components/)
- **스타일**: `tsconfig.json`의 strict 모드 활성화
- **인터페이스**: Props는 명시적 인터페이스 정의
- **네이밍**: 컴포넌트는 PascalCase, 파일명은 kebab-case

```tsx
interface AppProps {
  message?: string;
}

function App({ message = "Hello from React!" }: AppProps) {
  // ...
}
```

### 네이밍 컨벤션

- **Widget ID**: `kebab-case` (예: `example-widget`, `my-widget`)
- **폴더명**: `kebab-case` (예: `src/example/`, `src/solar-system/`)
- **React 컴포넌트**: `PascalCase` (예: `App`, `MyWidget`)
- **Python 함수**: `snake_case` (예: `_load_widget_html`)

### 포맷 규칙

- **들여쓰기**: Python/TypeScript 모두 2 spaces
- **최대 줄 길이**: 100자 (Python), 120자 (TypeScript)
- **문자열**: Python은 double quotes, TypeScript는 single quotes 권장

## 7. Common Commands

### 초기 설정
```bash
npm run install:all          # 모든 의존성 설치 (Python + Node)
npm run install:components   # React 의존성만 설치
npm run install:server       # Python 의존성만 설치
```

### 빌드
```bash
npm run build                # React 컴포넌트 빌드 (components/assets/ 생성)
npm run build:watch          # Watch 모드로 빌드 (자동 재빌드)
```

### 서버 실행
```bash
npm run server               # MCP 서버 시작 (http://0.0.0.0:8000)
npm run dev                  # 빌드 + 서버 실행 (한 번에)
```

### 개발 워크플로우
```bash
# 터미널 1: Watch 모드로 빌드
npm run build:watch

# 터미널 2: 서버 실행 (자동 reload)
npm run server

# 코드 수정 → 자동 빌드/재시작
```

### 유틸리티
```bash
# 빌드 결과 확인
ls -lh components/assets/

# 서버 로그 확인 (백그라운드 실행 시)
tail -f server.log

# 포트 사용 확인
lsof -i :8000

# 서버 강제 종료
pkill -f "python main.py"
```

## 8. Integration / APIs

### MCP Protocol
- **엔드포인트**: `http://localhost:8000`
- **전송 방식**: HTTP/SSE (Server-Sent Events)
- **프로토콜**: MCP (Model Context Protocol)

### 환경 변수 설정

서버는 환경 변수로 설정을 커스터마이즈할 수 있습니다:

```bash
# 서버 설정
HTTP_HOST=127.0.0.1        # 기본: 0.0.0.0
HTTP_PORT=9000             # 기본: 8000

# 로깅 레벨
LOG_LEVEL=DEBUG            # 기본: INFO (DEBUG, INFO, WARNING, ERROR, CRITICAL)

# 예시: 다른 포트로 서버 실행
HTTP_PORT=9000 npm run server

# 예시: 디버그 모드
LOG_LEVEL=DEBUG npm run server
```

### OpenAI Widget Metadata
MCP 응답에 포함되는 특수 메타데이터:

```python
_meta = {
    "openai.com/widget": widget_resource.model_dump(mode="json"),
    "openai/outputTemplate": widget.template_uri,
    "openai/toolInvocation/invoking": "Loading widget...",
    "openai/toolInvocation/invoked": "Widget loaded",
    "openai/widgetAccessible": True,
    "openai/resultCanProduceWidget": True,
}
```

### Asset Serving
- **개발 환경**: `http://localhost:4444` (serve 사용)
- **BASE_URL 환경 변수**: 빌드 시 asset 경로 설정 가능

```bash
BASE_URL=http://your-domain.com:4444 npm run build
```

## 9. Testing

프로젝트는 종합적인 테스트 커버리지를 제공합니다:

### Unit Tests (유닛 테스트)

캐시 모듈 및 엔드포인트 테스트:

```bash
# 가상환경 활성화
source .venv/bin/activate

# 캐시 모듈 유닛 테스트 실행
pytest tests/test_cache.py -v

# 엔드포인트 유닛 테스트
pytest server/tests/unit/ -v
```

**테스트 커버리지**:
- `tests/test_cache.py`: TTL 캐시 동작 (18개 테스트)
- `server/tests/unit/test_endpoints.py`: 엔드포인트 설정
- `server/tests/unit/test_client_endpoints.py`: 클라이언트 엔드포인트

### Integration Tests (통합 테스트)

전체 MCP 서버 테스트:

```bash
# MCP 서버 통합 테스트 실행
.venv/bin/python server/tests/test_mcp.py

# 스포츠 툴 테스트
.venv/bin/python server/tests/test_sports_tools.py

# Sports API 통합 테스트
.venv/bin/python server/tests/test_sports_api_integration.py
```

**테스트 커버리지** (`server/tests/test_mcp.py`):
- ✅ 위젯 로딩 (2개 위젯)
- ✅ 도구 로딩 (2개 도구: get_games_by_sport, get_game_details)
- ✅ MCP 프로토콜 도구 리스트
- ✅ MCP 프로토콜 리소스 리스트
- ✅ 위젯 도구 실행 (get_game_details)
- ✅ 텍스트 도구 실행 (get_games_by_sport)
- ✅ 리소스 읽기 (위젯 HTML)

**결과**: Sports MCP 기능 테스트 통과

### 테스트 전략

- **유닛 테스트**: 캐시, 엔드포인트 등 개별 모듈 테스트
- **통합 테스트**: 실제 MCP 프로토콜 흐름 검증
- **스포츠 API 테스트**: 4개 스포츠 (basketball, soccer, volleyball, football) API 통합

## 10. Important Notes

### ⚠️ 주의사항

1. **빌드 필수**: React 컴포넌트를 수정한 후 **반드시** `npm run build` 실행해야 MCP 서버가 새 HTML을 읽음

2. **Assets 경로**: 서버는 상대 경로로 assets를 찾음:
   ```python
   ASSETS_DIR = Path(__file__).resolve().parent.parent / "components" / "assets"
   ```
   - 서버를 다른 위치에서 실행하면 assets를 못 찾음
   - **항상 프로젝트 루트에서 실행**: `npm run server`

3. **가상환경 활성화**: Python 패키지는 `.venv`에 설치됨
   - `npm run server`는 `.venv/bin/python` 사용
   - 수동 실행 시: `source .venv/bin/activate` 필요

4. **포트 충돌**: 8000번 포트가 이미 사용 중이면 서버 시작 실패
   - `main.py`에서 포트 번호 변경 가능

5. **Node.js 버전**: Vite 7은 Node.js 20+ 권장
   - 현재 18.19.1로 동작하지만 경고 발생
   - 문제 발생 시 Node.js 업그레이드 필요

### 🚫 금지 패턴

- **빌드 없이 서버 실행**: `components/assets/`가 비어있으면 서버 시작 실패
- **직접 HTML 수정**: `assets/*.html`은 자동 생성되므로 수정 금지 (빌드 시 덮어씀)
- **system Python 사용**: 반드시 `.venv`의 Python 사용
- **components/ 내에서 서버 실행**: 경로 문제 발생

## 11. Tasks or Goals

### 현재 구현된 기능
✅ FastMCP 2.0 기반 MCP 서버 (레이어드 아키텍처)
✅ 팩토리 패턴으로 테스트 용이성 확보
✅ 환경 변수 기반 설정 (Config 클래스, .env.development / .env.production)
✅ 구조화된 로깅 (DEBUG/INFO/WARNING 레벨)
✅ React 컴포넌트 빌드 파이프라인
✅ Tailwind CSS + Zod 통합
✅ Example Widget (props 전달 + 검증)
✅ Hot Reload (서버 자동 재시작)
✅ 통합 테스트 스위트 (server/tests/)
✅ TTL 캐시 (게임 목록 API 응답 5분 캐싱)
✅ Sports API 통합 (4개 스포츠: basketball, soccer, volleyball, football)
✅ get_games_by_sport 툴 (텍스트 모드, TTL 캐시)
✅ get_game_details 툴 (Game Result Viewer 위젯, 모든 스포츠 지원)
✅ 스포츠별 모듈화 (Factory 패턴, endpoints.py)

### 우선순위 작업

#### 1. 서버 테스트
```bash
# Python 테스트 스크립트 실행
.venv/bin/python server/tests/test_mcp.py

# 스포츠 툴 테스트
.venv/bin/python server/tests/test_sports_tools.py

# 캐시 테스트
pytest tests/test_cache.py -v
```

테스트 항목:
- Widget 로딩 (2개)
- Tools 리스트 (2개)
- Resources 리스트
- Tool 호출 (props 전달)
- Resource 읽기

#### 2. 새 위젯 추가
사용자가 새로운 위젯을 요청하면:

1. `components/src/[widget-name]/index.tsx` 생성
2. React 컴포넌트 작성 (Zod 스키마 포함)
3. `npm run build` 실행
4. `server/main.py`의 `build_widgets()` 함수에 추가:
   ```python
   def build_widgets(cfg: Config) -> list[Widget]:
       example_html = load_widget_html("example", str(cfg.assets_dir))
       new_widget_html = load_widget_html("widget-name", str(cfg.assets_dir))  # 추가

       return [
           Widget(...),  # 기존
           Widget(  # 새 위젯
               identifier="widget-name",
               title="Widget Title",
               template_uri="ui://widget/widget-name.html",
               invoking="Loading widget...",
               invoked="Widget loaded",
               html=new_widget_html,
               response_text="Rendered widget!",
           ),
       ]
   ```

#### 3. Props 스키마 수정
위젯의 입력 스키마를 변경할 때:

1. `ToolInput` Pydantic 모델 수정 또는 새 모델 생성
2. `TOOL_INPUT_SCHEMA` 업데이트
3. `_call_tool_request`에서 `structuredContent` 설정
4. React 컴포넌트의 `Props` 인터페이스 동기화

#### 4. 디버깅
문제 발생 시 우선 확인:
- `components/assets/` 폴더에 HTML 파일 존재 여부
- 서버 콘솔 로그 확인 (로깅 레벨: INFO, WARNING, DEBUG)
  ```bash
  # 디버그 모드로 서버 실행
  LOG_LEVEL=DEBUG npm run server
  ```
- `npm run build` 재실행
- 서버 재시작
- 테스트 스크립트 실행 (`python test_mcp.py`)

### 반복 작업
- 위젯 추가 시마다 빌드 → 서버 등록 → 테스트
- Props 변경 시 Python + TypeScript 인터페이스 동기화 확인

## 12. Persona or Tone

### 커뮤니케이션 스타일
- **언어**: 한국어 (코드 내 주석/문서는 영어 가능)
- **톤**: 친근하고 명확한 설명, 기술적 정확성 유지
- **코드 리뷰**: 개선점을 제안할 때는 이유와 예시 포함

### 응답 패턴
- 명령어 실행 전 간단히 설명
- 오류 발생 시 원인과 해결 방법 명시
- 파일 수정 시 변경 사항 요약 제공

### 예시
```
좋은 질문입니다! 새 위젯을 추가하려면 3단계가 필요합니다:
1. React 컴포넌트 생성
2. 빌드
3. 서버에 등록

먼저 컴포넌트를 만들겠습니다...
```

---

**마지막 업데이트**: 2026-01-07
**프로젝트 버전**: 3.4.0 (Phase 7-8 완료, 문서 동기화)
