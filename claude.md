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

## 3. Folder Structure

```
test-mcp-server/
├── .venv/                      # Python 가상환경
├── server/                     # Python MCP 서버
│   ├── main.py                # 서버 엔트리포인트
│   │                          # - Widget 정의
│   │                          # - MCP tools/resources 등록
│   │                          # - HTTP/SSE 앱 설정
│   └── requirements.txt       # Python 의존성
│
├── components/                 # React 컴포넌트
│   ├── src/                   # React 소스 코드
│   │   ├── index.css          # 글로벌 CSS (Tailwind import)
│   │   └── example/           # 예제 위젯
│   │       └── index.tsx      # 컴포넌트 엔트리포인트
│   │
│   ├── assets/                # 빌드 결과물 (생성됨)
│   │   ├── example.html       # MCP 서버가 읽는 HTML
│   │   ├── example-9252.js    # 해시된 JS 번들
│   │   └── example-9252.css   # 해시된 CSS
│   │
│   ├── package.json           # Node 의존성
│   ├── tsconfig.json          # TypeScript 설정
│   ├── tailwind.config.ts     # Tailwind 설정
│   ├── vite.config.ts         # Vite 설정 (dev용)
│   └── build.ts               # 프로덕션 빌드 스크립트
│
├── package.json               # 루트 빌드 스크립트
├── .gitignore
├── README.md                  # 사용자 문서
└── claude.md                  # 이 파일 (Claude용 컨텍스트)
```

### 파일 역할 요약

| 파일 | 역할 |
|------|------|
| `server/main.py` | MCP 서버 로직 (레이어드 아키텍처) |
| │ - Configuration | Config 클래스, 환경 변수 관리 |
| │ - Logging | 구조화된 로깅 설정 |
| │ - Domain models | Widget, ToolInput 스키마 |
| │ - Assets loading | HTML 파일 로딩 (캐싱) |
| │ - Widget registry | 위젯 빌드 및 인덱싱 |
| │ - Metadata helpers | OpenAI 메타데이터 생성 |
| │ - MCP server | 팩토리 함수로 서버 생성 |
| │ - App factory | ASGI 앱 생성 (CORS 포함) |
| `components/src/*/index.tsx` | React 컴포넌트 (빌드 대상) |
| `components/build.ts` | Vite 빌드 스크립트 (해시 생성, HTML 생성) |
| `components/assets/*.html` | Python이 읽어서 MCP 리소스로 전달 |
| `package.json` (루트) | 통합 빌드 스크립트 |
| `test_mcp.py` | MCP 서버 기능 테스트 스크립트 |

## 4. Development Guidelines

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

## 5. Common Commands

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

## 6. Integration / APIs

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

## 7. Important Notes

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

## 8. Tasks or Goals

### 현재 구현된 기능
✅ FastMCP 2.0 기반 MCP 서버 (레이어드 아키텍처)
✅ 팩토리 패턴으로 테스트 용이성 확보
✅ 환경 변수 기반 설정 (Config 클래스)
✅ 구조화된 로깅 (DEBUG/INFO/WARNING 레벨)
✅ React 컴포넌트 빌드 파이프라인
✅ Tailwind CSS + Zod 통합
✅ Example Widget (props 전달 + 검증)
✅ Hot Reload (서버 자동 재시작)
✅ Python 테스트 스크립트 (test_mcp.py)

### 우선순위 작업

#### 1. 서버 테스트
```bash
# Python 테스트 스크립트 실행
python test_mcp.py

# 또는 가상환경에서
.venv/bin/python test_mcp.py
```

테스트 항목:
- Widget 로딩
- Tools 리스트
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

## 9. Persona or Tone

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

**마지막 업데이트**: 2025-10-30
**프로젝트 버전**: 1.1.0 (레이어드 아키텍처, 팩토리 패턴, 환경 변수 설정)
