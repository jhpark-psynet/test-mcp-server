# Test MCP Server Architecture

**작성일**: 2025-11-04
**목적**: 프로젝트의 핵심 설계 패턴 및 아키텍처 결정 사항 문서화

---

## 목차

1. [SafeFastMCPWrapper 패턴](#safefastmcpwrapper-패턴)
2. [External API 툴 관리 구조](#external-api-툴-관리-구조)
3. [레이어드 아키텍처](#레이어드-아키텍처)

---

## SafeFastMCPWrapper 패턴

### 의도 (Intent)

FastMCP 라이브러리의 **비공개 내부 API**(`_mcp_server`)에 안전하게 접근하기 위한 래퍼 패턴입니다. 라이브러리 업데이트로 인한 내부 구조 변경을 조기에 감지하고, 명확한 에러 메시지를 통해 빠른 대응이 가능하도록 합니다.

### 문제점 (Problem)

#### FastMCP 내부 API 직접 사용의 위험성

```python
# ❌ 위험한 코드: 비공개 API 직접 접근
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("My Server")

# 비공개 속성 직접 접근
mcp._mcp_server.list_tools()(my_handler)
mcp._mcp_server.request_handlers[types.CallToolRequest] = handler
```

**발생 가능한 문제**:

1. **런타임 크래시**
   ```python
   # FastMCP 2.0 → 2.1 업데이트 후
   AttributeError: 'FastMCP' object has no attribute '_mcp_server'
   # 🔥 서버 전체 다운!
   ```

2. **불명확한 에러 메시지**
   ```
   AttributeError: 'FastMCP' object has no attribute '_mcp_server'
   # 🤔 무엇을 해야 하는지 알 수 없음
   ```

3. **여러 곳에 흩어진 의존성**
   - 코드 전체에 `_mcp_server` 접근이 산재
   - FastMCP 변경 시 모든 위치를 수정해야 함

### 해결 방법 (Solution)

#### SafeFastMCPWrapper 구현

**파일**: `server/factory/safe_wrapper.py`

```python
class SafeFastMCPWrapper:
    """FastMCP 비공개 API 접근을 안전하게 래핑.

    FastMCP 내부 구조 변경을 감지하고 명확한 에러 메시지를 제공합니다.
    """

    def __init__(self, mcp: FastMCP):
        """Initialize wrapper.

        Args:
            mcp: FastMCP instance to wrap

        Raises:
            FastMCPInternalAPIError: If FastMCP internal structure is incompatible
        """
        self._mcp = mcp
        self._validate_internal_api()  # ← 서버 시작 시 즉시 검증

    def _validate_internal_api(self) -> None:
        """FastMCP 내부 구조 검증."""
        if not hasattr(self._mcp, '_mcp_server'):
            raise FastMCPInternalAPIError(
                "FastMCP internal structure changed: '_mcp_server' attribute not found. "
                "This may be due to a FastMCP version update. "
                "Please check the FastMCP changelog and update the wrapper."
            )

        if not hasattr(self._mcp._mcp_server, 'request_handlers'):
            raise FastMCPInternalAPIError(
                "FastMCP internal structure changed: 'request_handlers' attribute not found."
            )

    def list_tools_decorator(self) -> Callable:
        """Get list_tools decorator safely."""
        try:
            return self._mcp._mcp_server.list_tools
        except AttributeError as e:
            raise FastMCPInternalAPIError(
                f"FastMCP 'list_tools' decorator not found: {e}. "
                "The FastMCP API may have changed."
            ) from e

    def register_request_handler(
        self,
        request_type: type,
        handler: Callable
    ) -> None:
        """Register a request handler safely."""
        try:
            self._mcp._mcp_server.request_handlers[request_type] = handler
        except (AttributeError, KeyError, TypeError) as e:
            raise FastMCPInternalAPIError(
                f"Failed to register handler for {request_type.__name__}: {e}."
            ) from e
```

### 사용법 (Usage)

#### 기본 사용

**파일**: `server/factory/server_factory.py`

```python
from mcp.server.fastmcp import FastMCP
from server.factory.safe_wrapper import SafeFastMCPWrapper

def create_mcp_server(cfg: Config) -> FastMCP:
    # 1. FastMCP 인스턴스 생성
    mcp = FastMCP(
        name=cfg.app_name,
        stateless_http=True,
    )

    # 2. SafeFastMCPWrapper로 래핑
    wrapper = SafeFastMCPWrapper(mcp)
    # ← 이 시점에서 내부 API 검증 완료

    # 3. 안전한 메서드 사용
    @wrapper.list_tools_decorator()
    async def handle_list_tools() -> list[types.Tool]:
        return tools_payload

    # 4. 핸들러 등록
    wrapper.register_request_handler(
        types.CallToolRequest,
        handle_call_tool
    )

    return mcp
```

#### 에러 처리

```python
try:
    wrapper = SafeFastMCPWrapper(mcp)
except FastMCPInternalAPIError as e:
    logger.error(f"FastMCP compatibility issue: {e}")
    # FastMCP 버전 확인 및 래퍼 업데이트 필요
    raise
```

### 장점 (Benefits)

#### 1. **Fail-Fast 원칙**
```python
# 서버 시작 시 즉시 감지
wrapper = SafeFastMCPWrapper(mcp)
# ❌ FastMCP 구조 변경되었다면 여기서 에러 발생

# vs. 래퍼 없이:
# ✓ 서버 시작 성공
# ❌ 첫 요청 시 크래시
```

#### 2. **명확한 에러 메시지**
```python
# ❌ 래퍼 없이:
AttributeError: 'FastMCP' object has no attribute '_mcp_server'

# ✅ 래퍼 사용:
FastMCPInternalAPIError: FastMCP internal structure changed:
'_mcp_server' attribute not found. This may be due to a FastMCP
version update. Please check the FastMCP changelog and update
the wrapper.
```

#### 3. **변경 지점 격리**
```python
# FastMCP API 변경 시:
# - 래퍼 없이: 코드 전체에서 수정
# - 래퍼 사용: safe_wrapper.py 한 곳만 수정
```

#### 4. **테스트 용이성**
```python
# 단위 테스트: Wrapper 인터페이스만 모킹
mock_wrapper = Mock(spec=SafeFastMCPWrapper)
mock_wrapper.list_tools_decorator.return_value = lambda func: func

# vs. 래퍼 없이: FastMCP 내부 구조 전체 모킹 필요
```

### 트레이드오프 (Trade-offs)

**장점**:
- ✅ 안정성: FastMCP 업데이트에 안전
- ✅ 유지보수성: 변경이 한 곳에 격리
- ✅ 디버깅: 명확한 에러 메시지

**단점**:
- ⚠️ 추가 추상화 레이어
- ⚠️ FastMCP 변경 시 래퍼 업데이트 필요

**결정**: 안정성과 유지보수성이 더 중요하므로 래퍼 사용

---

## External API 툴 관리 구조

### 의도 (Intent)

외부 API 통합 기능을 **선택적(optional) 기능**으로 관리하여, 환경 설정에 따라 동적으로 툴을 등록하고 사용자에게 깔끔한 경험을 제공합니다.

### 설계 원칙 (Design Principles)

#### 1. **동적 툴 등록**

**필수 툴** vs **선택적 툴**:

```python
# server/services/tool_registry.py

def build_tools(cfg: Config) -> List[ToolDefinition]:
    tools = []

    # ✅ 필수 툴: 항상 등록
    tools.append(
        ToolDefinition(
            name="calculator",
            tool_type=ToolType.TEXT,
            handler=calculator_handler,
            ...
        )
    )

    # 🔀 선택적 툴: 설정에 따라 등록
    if cfg.has_external_api:
        tools.append(
            ToolDefinition(
                name="external-fetch",
                tool_type=ToolType.TEXT,
                handler=None,  # 특수 처리
                ...
            )
        )
        logger.info("External API tool registered: %s", cfg.external_api_base_url)
    else:
        logger.debug("External API not configured, skipping external-fetch tool")

    return tools
```

#### 2. **설정 기반 활성화**

**파일**: `server/config.py`

```python
class Config(BaseSettings):
    # External API 설정
    external_api_base_url: str = Field(
        default="",
        alias="EXTERNAL_API_BASE_URL",
    )

    external_api_key: str = Field(
        default="",
        alias="EXTERNAL_API_KEY",
    )

    external_api_timeout_s: float = Field(default=10.0, ...)
    external_api_auth_header: str = Field(default="Authorization", ...)
    external_api_auth_scheme: str = Field(default="Bearer", ...)

    @computed_field
    @property
    def has_external_api(self) -> bool:
        """Check if external API is configured."""
        return bool(self.external_api_base_url and self.external_api_key)
```

### 왜 별도로 관리하는가? (Why Separate Management?)

#### 이유 1: **선택적 의존성**

```python
# Calculator: 외부 의존성 없음
calculator(expression: str) -> str
    # 로컬에서 계산
    # 항상 작동

# External-fetch: 외부 의존성 있음
external_fetch(query: str, ...) -> Result
    # 외부 API 호출 필요
    # URL + API Key 필요
    # 네트워크 연결 필요
```

#### 이유 2: **사용자 경험**

```python
# ❌ 나쁜 UX: 항상 등록
tools.append(external_fetch_tool)

# ChatGPT에서:
👤 "외부 API에서 데이터 가져와줘"
🤖 [external-fetch 툴 호출]
❌ Error: External API not configured
# 사용자 혼란, 불필요한 에러


# ✅ 좋은 UX: 설정 있을 때만 등록
if cfg.has_external_api:
    tools.append(external_fetch_tool)

# ChatGPT에서 (설정 없으면):
# external-fetch 툴이 아예 목록에 없음
# 사용 가능한 툴만 표시
```

#### 이유 3: **환경별 다른 설정**

```bash
# 개발 환경
# .env 파일 없음
npm run server
# → calculator만 사용 가능

# 프로덕션 환경
# .env
EXTERNAL_API_BASE_URL=https://api.company.com
EXTERNAL_API_KEY=prod-key-xyz
npm run server
# → calculator + external-fetch 사용 가능
```

#### 이유 4: **보안**

```python
# API Key가 없으면 툴 자체가 등록 안 됨
if cfg.has_external_api:  # URL과 Key 모두 필요
    tools.append(external_fetch_tool)
else:
    # 툴 없음 → 사용 시도 불가능
    # → 불필요한 네트워크 요청 없음
    # → API Key 노출 위험 없음
```

#### 이유 5: **테스트 용이성**

```python
# test_mcp.py

async def test_external_fetch():
    """Test external API fetch tool (if configured)."""

    # 설정 없으면 테스트 스킵
    if not CONFIG.has_external_api:
        print("⏭️  External API not configured, skipping test")
        return None

    # 설정 있으면 테스트 실행
    ...

# 결과:
# - 설정 없어도 테스트 통과 (7/9)
# - 설정 있으면 전체 테스트 통과 (9/9)
```

### handler=None의 의미 (Why handler=None?)

#### 일반 툴 vs External-Fetch 툴

```python
# ✅ Calculator: 단순 → handler 패턴
ToolDefinition(
    name="calculator",
    handler=calculator_handler,  # 간단한 함수
)

# server_factory.py
elif tool.is_text_tool and tool.handler:
    result_text = tool.handler(validated_args)
    return TextContent(text=result_text)


# ❌ External-Fetch: 복잡 → 직접 처리
ToolDefinition(
    name="external-fetch",
    handler=None,  # 너무 복잡해서 handler로 처리 불가
)

# server_factory.py:262 - 특수 처리
elif tool.name == "external-fetch":
    # 1. ExternalToolInput 검증
    payload = ExternalToolInput.model_validate(arguments)

    # 2. API 클라이언트 생성 (Config 필요)
    api_client = ExternalApiClient(
        base_url=cfg.external_api_base_url,
        api_key=cfg.external_api_key,
        timeout_seconds=cfg.external_api_timeout_s,
        ...
    )

    # 3. 비동기 HTTP 호출
    data = await api_client.fetch_json(query, params=params)

    # 4. text/widget 모드 분기
    if response_mode == "text":
        return TextContent(...)
    else:
        return CallToolResult(
            structuredContent={"success": True, "data": data, ...},
            _meta={"openai.com/widget": widget_resource, ...}
        )

    # 5. 에러 타입별 처리
    except ApiTimeoutError:
        ...
    except ApiHttpError:
        ...
    except ApiConnectionError:
        ...
```

**handler로 처리 불가능한 이유**:
1. **Config 의존성**: API 클라이언트 생성에 5개 설정 필요
2. **비동기 처리**: `async/await` 필요
3. **복잡한 분기**: text/widget 모드에 따라 완전히 다른 응답
4. **위젯 메타데이터**: 복잡한 OpenAI 위젯 스펙 처리
5. **에러 처리**: 3가지 에러 타입별 다른 처리

### 사용법 (Usage)

#### 환경 설정

```bash
# .env
EXTERNAL_API_BASE_URL=https://jsonplaceholder.typicode.com
EXTERNAL_API_KEY=your-api-key-here
EXTERNAL_API_TIMEOUT_S=10
EXTERNAL_API_AUTH_HEADER=Authorization
EXTERNAL_API_AUTH_SCHEME=Bearer
```

#### 툴 호출 (ChatGPT에서)

```python
# Text 모드
👤 "JSONPlaceholder에서 사용자 1번 정보 가져와줘"
🤖 [external-fetch 툴 호출]
    {
        "query": "/users/1",
        "response_mode": "text"
    }
📄 텍스트 응답:
   """
   Endpoint: /users/1
   Status: Success
   Data: {...}
   """

# Widget 모드
👤 "JSONPlaceholder에서 포스트 목록 가져와서 보기 좋게 보여줘"
🤖 [external-fetch 툴 호출]
    {
        "query": "/posts",
        "response_mode": "widget"
    }
📊 위젯 렌더링:
   [api-result React 컴포넌트]
   - 초록색 성공 UI
   - 데이터 요약
   - JSON 프리뷰
   - "Show Raw JSON" 토글
```

#### 새로운 선택적 툴 추가

```python
# 1. Config에 설정 추가
class Config(BaseSettings):
    weather_api_url: str = Field(default="", ...)
    weather_api_key: str = Field(default="", ...)

    @computed_field
    @property
    def has_weather_api(self) -> bool:
        return bool(self.weather_api_url and self.weather_api_key)

# 2. 툴 등록
def build_tools(cfg: Config) -> List[ToolDefinition]:
    tools = []

    # 필수 툴들...

    # 선택적 툴: 날씨 API
    if cfg.has_weather_api:
        tools.append(
            ToolDefinition(
                name="weather-fetch",
                handler=None,  # 복잡하면 None
                ...
            )
        )

    return tools

# 3. server_factory.py에 핸들러 추가
elif tool.name == "weather-fetch":
    # 특수 처리 로직
    ...
```

### 장점 (Benefits)

#### 1. **깔끔한 UX**
- 사용 가능한 툴만 표시
- 불필요한 에러 없음

#### 2. **환경별 유연성**
- 개발: 최소 기능
- 스테이징: 일부 통합
- 프로덕션: 전체 기능

#### 3. **보안 강화**
- API Key 없으면 툴 자체가 없음
- 조기 차단 (서버 시작 시)

#### 4. **테스트 독립성**
- 외부 API 없어도 핵심 기능 테스트 가능
- 통합 테스트는 선택적

#### 5. **명확한 로그**
```
INFO  External API: ✓ Configured
INFO  External API tool registered: https://api.example.com

# vs.

INFO  External API: ✗ Not configured
DEBUG External API not configured, skipping external-fetch tool
```

### 트레이드오프 (Trade-offs)

**장점**:
- ✅ 유연성: 환경별 다른 설정
- ✅ 안정성: 설정 검증 조기 차단
- ✅ UX: 깔끔한 툴 목록

**단점**:
- ⚠️ 복잡성: 동적 등록 로직 추가
- ⚠️ 특수 처리: handler=None 툴은 직접 구현

**결정**: 프로덕션 환경의 유연성과 안정성이 더 중요하므로 동적 등록 사용

---

## 레이어드 아키텍처

### 개요

모듈화된 레이어드 아키텍처로 관심사를 명확히 분리합니다.

```
server/
├── main.py                 # 진입점 (32줄)
├── config.py               # 설정 관리
├── logging_config.py       # 로깅 설정
│
├── models/                 # 도메인 모델
│   ├── widget.py          # Widget, ToolType
│   ├── tool.py            # ToolDefinition
│   └── schemas.py         # Pydantic 스키마
│
├── services/              # 비즈니스 로직
│   ├── asset_loader.py
│   ├── widget_registry.py
│   ├── tool_registry.py
│   ├── metadata_builder.py
│   ├── response_formatter.py
│   ├── api_client.py
│   └── exceptions.py
│
├── handlers/              # 툴 핸들러
│   ├── calculator.py      # AST 기반 안전한 계산기
│   └── external_fetch.py  # (현재 server_factory에 통합)
│
└── factory/               # MCP 서버 팩토리
    ├── server_factory.py  # MCP 서버 생성
    ├── safe_wrapper.py    # SafeFastMCPWrapper
    └── metadata_builder.py
```

### 의존성 방향

```
main.py
  ↓
factory/ (server_factory)
  ↓
services/ + handlers/
  ↓
models/
```

---

## 참조

- [REFACTORING_PLAN.md](./REFACTORING_PLAN.md) - 전체 리팩토링 계획
- [IMPROVEMENT_RECOMMENDATIONS.md](./IMPROVEMENT_RECOMMENDATIONS.md) - 개선 제안 및 완료 상태
- [README.md](./README.md) - 프로젝트 개요 및 사용법
- [claude.md](./claude.md) - 상세 문서

---

**마지막 업데이트**: 2025-11-04
**작성자**: Claude Code (with junho)
