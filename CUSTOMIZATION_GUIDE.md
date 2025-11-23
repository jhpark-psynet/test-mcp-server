# Customization Guide

**목적**: 테스트 프로젝트를 실제 사용 사례에 맞게 커스터마이징하는 방법

이 가이드는 example 위젯을 **실제 비즈니스 로직**으로 교체하고 새로운 툴을 추가하는 방법을 단계별로 안내합니다.

**현재 프로젝트 상태**:
- Sports MCP 툴 2개: `get_games_by_sport`, `get_game_details`
- 위젯 3개: `example` (테스트용), `game-result-viewer`, `game-stats`
- `example` 위젯은 툴 목록에서 제외됨 (테스트용으로 코드만 유지)

---

## 목차

1. [새로운 위젯 추가하기](#1-새로운-위젯-추가하기)
2. [새로운 툴 추가하기](#2-새로운-툴-추가하기)
3. [외부 API 통합하기](#3-외부-api-통합하기)
4. [테스트하기](#4-테스트하기)
5. [배포 준비하기](#5-배포-준비하기)

---

## 1. 새로운 위젯 추가하기

### 예제: 날씨 정보 위젯

실제 사용 사례: **날씨 API 데이터를 시각화하는 위젯**

#### Step 1.1: React 컴포넌트 작성

**파일**: `components/src/weather/index.tsx`

```bash
mkdir -p components/src/weather
```

```tsx
// components/src/weather/index.tsx
import { createRoot } from 'react-dom/client';
import { useState, useEffect } from 'react';
import { z } from 'zod';

// Props 스키마 정의
const WeatherPropsSchema = z.object({
  city: z.string(),
  temperature: z.number(),
  condition: z.string(),
  humidity: z.number().optional(),
  windSpeed: z.number().optional(),
});

type WeatherProps = z.infer<typeof WeatherPropsSchema>;

function WeatherWidget(props: WeatherProps) {
  // Props 검증
  const validated = WeatherPropsSchema.parse(props);

  const { city, temperature, condition, humidity, windSpeed } = validated;

  // 날씨 상태에 따른 이모지
  const getWeatherEmoji = (condition: string) => {
    const lower = condition.toLowerCase();
    if (lower.includes('sun') || lower.includes('clear')) return '☀️';
    if (lower.includes('cloud')) return '☁️';
    if (lower.includes('rain')) return '🌧️';
    if (lower.includes('snow')) return '❄️';
    return '🌤️';
  };

  return (
    <div className="min-h-[200px] p-6 bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg">
      {/* 헤더 */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold text-blue-900">{city}</h2>
        <span className="text-5xl">{getWeatherEmoji(condition)}</span>
      </div>

      {/* 온도 */}
      <div className="text-center mb-6">
        <div className="text-6xl font-bold text-blue-900">
          {Math.round(temperature)}°C
        </div>
        <div className="text-xl text-blue-700 mt-2">{condition}</div>
      </div>

      {/* 추가 정보 */}
      <div className="grid grid-cols-2 gap-4 text-sm">
        {humidity !== undefined && (
          <div className="bg-white/50 rounded p-3">
            <div className="text-blue-600 font-semibold">Humidity</div>
            <div className="text-blue-900 text-lg">{humidity}%</div>
          </div>
        )}
        {windSpeed !== undefined && (
          <div className="bg-white/50 rounded p-3">
            <div className="text-blue-600 font-semibold">Wind Speed</div>
            <div className="text-blue-900 text-lg">{windSpeed} km/h</div>
          </div>
        )}
      </div>
    </div>
  );
}

// 에러 폴백
function ErrorFallback({ error }: { error: Error }) {
  return (
    <div className="p-4 bg-red-50 border border-red-200 rounded">
      <h3 className="text-red-800 font-bold">Weather Widget Error</h3>
      <p className="text-red-600 text-sm mt-2">{error.message}</p>
    </div>
  );
}

// Wrapper component with loading state
function WeatherApp() {
  const [weatherData, setWeatherData] = useState<WeatherProps | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const updateData = () => {
      try {
        const rawData = (window as any).openai?.toolOutput;

        // 데이터가 아직 없으면 로딩 상태 유지
        // ⚠️ 중요: MOCK 데이터를 사용하지 마세요!
        if (!rawData || (typeof rawData === 'object' && Object.keys(rawData).length === 0)) {
          return;
        }

        const validatedData = WeatherPropsSchema.parse(rawData);
        setWeatherData(validatedData);
        setError(null);
      } catch (err) {
        if (err instanceof z.ZodError) {
          setError(err.errors.map(e => `${e.path.join('.')}: ${e.message}`).join('\n'));
        } else {
          setError(String(err));
        }
      }
    };

    // 초기 데이터 로드
    updateData();

    // window.openai.toolOutput 변경 감지 (100ms 폴링)
    const intervalId = setInterval(updateData, 100);

    return () => clearInterval(intervalId);
  }, []);

  if (error) {
    return <ErrorFallback error={new Error(error)} />;
  }

  if (!weatherData) {
    return (
      <div className="min-h-[200px] p-6 bg-gray-50 rounded-lg flex items-center justify-center">
        <p className="text-gray-600">Loading weather data...</p>
      </div>
    );
  }

  return <WeatherWidget {...weatherData} />;
}

// DOM 마운트
const rootElement = document.getElementById('weather-root');
if (rootElement) {
  const root = createRoot(rootElement);
  root.render(<WeatherApp />);
}

export default WeatherWidget;
```

#### Step 1.2: 빌드 설정 확인

`components/build.ts`는 자동으로 `src/` 폴더의 모든 위젯을 빌드합니다.

**기본 빌드 (content hashing 비활성화)**:
```bash
npm run build
```

**프로덕션 빌드 (content hashing 활성화)**:
```bash
USE_HASH=true npm run build
```

**빌드 모드 선택 가이드**:
- **기본값 (권장)**: `npm run build`
  - 단순 파일명 (`weather.js`)
  - 디버깅 용이
  - 빠른 반복 개발
  - 대부분의 배포 환경에 적합

- **프로덕션 (해시 필요 시)**: `USE_HASH=true npm run build`
  - 파일명에 SHA-256 해시 포함 (`weather-a1b2c3d4.js`)
  - 브라우저 캐시 무효화 자동 처리
  - CDN 배포 시 권장

**예상 출력 (기본 모드)**:
```
Building weather...
  JS:  weather.js
  CSS: weather.css
✓ Built weather

Build Summary
============================================================
Widgets built: 3
Output directory: assets/

Artifacts:
  weather:
    JS:  weather.js
    CSS: weather.css
    HTML: weather.html
============================================================

Hash mode: disabled
```

**예상 출력 (해시 모드)**:
```
Building weather...
  JS:  weather.js -> weather-a1b2c3d4.js
  CSS: weather.css -> weather-e5f6g7h8.css
✓ Built weather

Build Summary
============================================================
Widgets built: 3
Output directory: assets/

Artifacts:
  weather:
    JS:  weather-a1b2c3d4.js
    CSS: weather-e5f6g7h8.css
    HTML: weather.html
============================================================

Hash mode: enabled
```

#### Step 1.3: 서버에 위젯 등록

**파일**: `server/services/widget_registry.py`

```python
# server/services/widget_registry.py

def build_widgets(cfg: Config) -> List[Widget]:
    """Build widget registry from HTML assets."""
    widgets = []

    # 기존 위젯들...

    # 날씨 위젯 추가
    widgets.append(
        Widget(
            identifier="weather",
            title="Weather Widget",
            template_uri="ui://widget/weather.html",
            invoking="Loading weather information...",
            invoked="Weather information loaded",
            html=load_widget_html("weather", cfg.assets_dir),
            response_text="Rendered weather widget",
        )
    )

    logger.info("Loaded %d widget(s)", len(widgets))
    return widgets
```

#### Step 1.4: 위젯 기반 툴 추가

**파일**: `server/services/tool_registry.py`

```python
# server/services/tool_registry.py

def build_tools(cfg: Config) -> List[ToolDefinition]:
    tools = []
    widgets = build_widgets(cfg)
    widgets_by_id = {w.identifier: w for w in widgets}

    # 기존 툴들...

    # 날씨 위젯 툴 추가
    if "weather" in widgets_by_id:
        tools.append(
            ToolDefinition(
                name="weather-widget",
                title="Weather Widget",
                description="Display weather information with an interactive widget",
                input_schema={
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "City name"
                        },
                        "temperature": {
                            "type": "number",
                            "description": "Temperature in Celsius"
                        },
                        "condition": {
                            "type": "string",
                            "description": "Weather condition (e.g., Sunny, Cloudy, Rainy)"
                        },
                        "humidity": {
                            "type": "number",
                            "description": "Humidity percentage (optional)"
                        },
                        "windSpeed": {
                            "type": "number",
                            "description": "Wind speed in km/h (optional)"
                        }
                    },
                    "required": ["city", "temperature", "condition"]
                },
                tool_type=ToolType.WIDGET,
                widget=widgets_by_id["weather"],
                invoking="Loading weather widget...",
                invoked="Weather widget loaded",
            )
        )

    return tools
```

#### Step 1.5: 테스트

**통합 테스트**:

```bash
# 서버 실행
npm run server

# 별도 터미널에서 테스트
python test_mcp.py
```

**수동 테스트** (Python 스크립트):

```python
# test_weather_widget.py
import asyncio
import mcp.types as types
from server.config import CONFIG
from server.factory import create_mcp_server

async def test_weather_widget():
    mcp = create_mcp_server(CONFIG)

    # 위젯 툴 호출
    request = types.CallToolRequest(
        params=types.CallToolRequestParams(
            name="weather-widget",
            arguments={
                "city": "Seoul",
                "temperature": 15.5,
                "condition": "Sunny",
                "humidity": 60,
                "windSpeed": 12
            }
        )
    )

    # 핸들러 직접 호출
    handler = mcp._mcp_server.request_handlers.get(types.CallToolRequest)
    result = await handler(request)

    print("✓ Weather widget test passed")
    print(f"  structuredContent: {result.content[0].structuredContent}")

asyncio.run(test_weather_widget())
```

---

## 2. 새로운 툴 추가하기

### 2.1 단순 텍스트 툴

**예제: JSON 포맷터**

#### Step 2.1.1: 핸들러 작성

**파일**: `server/handlers/json_formatter.py`

```python
# server/handlers/json_formatter.py
"""JSON formatting tool handler."""
import json
from typing import Dict, Any


def json_formatter_handler(args: Dict[str, Any]) -> str:
    """Format JSON string with proper indentation.

    Args:
        args: Tool arguments containing 'json_string' and optional 'indent'

    Returns:
        Formatted JSON string or error message
    """
    json_string = args.get("expression", "")
    indent = args.get("indent", 2)

    try:
        # Parse JSON
        data = json.loads(json_string)

        # Format with indentation
        formatted = json.dumps(data, indent=indent, ensure_ascii=False)

        return f"Formatted JSON:\n```json\n{formatted}\n```"

    except json.JSONDecodeError as e:
        return f"Error: Invalid JSON - {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"
```

#### Step 2.1.2: 툴 등록

**파일**: `server/services/tool_registry.py`

```python
# server/services/tool_registry.py
from server.handlers.json_formatter import json_formatter_handler

# JSON_FORMATTER_INPUT_SCHEMA 정의
JSON_FORMATTER_INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "json_string": {
            "type": "string",
            "description": "JSON string to format"
        },
        "indent": {
            "type": "number",
            "description": "Indentation spaces (default: 2)",
            "default": 2
        }
    },
    "required": ["json_string"]
}

def build_tools(cfg: Config) -> List[ToolDefinition]:
    tools = []

    # 기존 툴들...

    # JSON 포맷터 추가
    tools.append(
        ToolDefinition(
            name="json-formatter",
            title="JSON Formatter",
            description="Format JSON string with proper indentation",
            input_schema=JSON_FORMATTER_INPUT_SCHEMA,
            tool_type=ToolType.TEXT,
            handler=json_formatter_handler,
            invoking="Formatting JSON...",
            invoked="JSON formatted",
        )
    )

    return tools
```

#### Step 2.1.3: Pydantic 스키마 추가 (선택사항)

**파일**: `server/models/schemas.py`

```python
# server/models/schemas.py
class JsonFormatterToolInput(BaseModel):
    """JSON formatter tool input schema."""
    json_string: str = Field(..., description="JSON string to format")
    indent: int = Field(2, ge=0, le=8, description="Indentation spaces")
```

**server_factory.py 수정**:

```python
# server/factory/server_factory.py
if tool.name == "json-formatter":
    payload = JsonFormatterToolInput.model_validate(arguments)
    validated_args = payload.model_dump()
```

### 2.2 복잡한 툴 (handler=None)

**예제: 데이터베이스 쿼리 툴**

복잡한 요구사항:
- 데이터베이스 연결 필요 (Config 의존)
- 비동기 처리
- text/widget 모드 분기
- 에러 타입별 처리

#### Step 2.2.1: 툴 정의

**파일**: `server/services/tool_registry.py`

```python
# DB 쿼리 툴 (설정 필요한 경우만)
if cfg.has_database:  # Config에 has_database 속성 추가 필요
    tools.append(
        ToolDefinition(
            name="database-query",
            title="Database Query",
            description="Execute database queries with result visualization",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "SQL query to execute"
                    },
                    "response_mode": {
                        "type": "string",
                        "enum": ["text", "widget"],
                        "default": "text",
                        "description": "Response format"
                    }
                },
                "required": ["query"]
            },
            tool_type=ToolType.TEXT,
            handler=None,  # 복잡한 처리 → 직접 구현
            invoking="Executing database query...",
            invoked="Query executed",
        )
    )
```

#### Step 2.2.2: 핸들러 구현

**파일**: `server/factory/server_factory.py`

```python
# server/factory/server_factory.py

# _call_tool_request 함수 내부에 추가
elif tool.name == "database-query":
    try:
        # 1. Input 검증
        payload = DatabaseQueryInput.model_validate(arguments)
        query = payload.query
        response_mode = payload.response_mode

        # 2. 데이터베이스 클라이언트 생성
        db_client = DatabaseClient(
            host=cfg.db_host,
            port=cfg.db_port,
            database=cfg.db_name,
            user=cfg.db_user,
            password=cfg.db_password,
        )

        # 3. 쿼리 실행
        results = await db_client.execute(query)
        await db_client.close()

        # 4. 응답 모드에 따라 분기
        if response_mode == "text":
            # 텍스트로 포맷
            result_text = format_query_results_text(results, query)
            return types.ServerResult(
                types.CallToolResult(
                    content=[types.TextContent(type="text", text=result_text)],
                    _meta=text_tool_meta(tool),
                )
            )
        else:
            # 위젯으로 반환
            widget = tools_by_name["query-result-widget"].widget
            widget_resource = embedded_widget_resource(cfg, widget)

            return types.ServerResult(
                types.CallToolResult(
                    content=[
                        types.TextContent(
                            type="text",
                            text=f"Query executed: {len(results)} rows"
                        )
                    ],
                    structuredContent={
                        "success": True,
                        "query": query,
                        "rows": results,
                        "count": len(results),
                    },
                    _meta={
                        "openai.com/widget": widget_resource.model_dump(mode="json"),
                        **widget_tool_meta(widget),
                    },
                )
            )

    except DatabaseError as exc:
        logger.error("Database error: %s", exc)
        return types.ServerResult(
            types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text=f"Database error: {str(exc)}"
                    )
                ],
                isError=True,
            )
        )
```

---

## 3. 외부 API 통합하기

### 3.1 환경 변수 설정

**파일**: `.env`

```bash
# .env

# 기본 설정
HTTP_HOST=0.0.0.0
HTTP_PORT=8000
LOG_LEVEL=INFO

# 외부 API 설정
EXTERNAL_API_BASE_URL=https://api.yourservice.com
EXTERNAL_API_KEY=your-secret-api-key-here
EXTERNAL_API_TIMEOUT_S=30
EXTERNAL_API_AUTH_HEADER=Authorization
EXTERNAL_API_AUTH_SCHEME=Bearer

# 또는 다른 인증 방식
# EXTERNAL_API_AUTH_HEADER=X-API-Key
# EXTERNAL_API_AUTH_SCHEME=ApiKey
```

### 3.2 Config 확장 (선택사항)

여러 외부 API를 사용하는 경우:

**파일**: `server/config.py`

```python
# server/config.py

class Config(BaseSettings):
    # 기존 설정들...

    # 날씨 API
    weather_api_url: str = Field(
        default="",
        alias="WEATHER_API_URL",
        description="Weather API URL"
    )

    weather_api_key: str = Field(
        default="",
        alias="WEATHER_API_KEY",
        description="Weather API key"
    )

    # 데이터베이스
    db_host: str = Field(
        default="localhost",
        alias="DB_HOST",
        description="Database host"
    )

    db_port: int = Field(
        default=5432,
        alias="DB_PORT",
        description="Database port"
    )

    # Computed properties
    @computed_field
    @property
    def has_weather_api(self) -> bool:
        """Check if weather API is configured."""
        return bool(self.weather_api_url and self.weather_api_key)

    @computed_field
    @property
    def has_database(self) -> bool:
        """Check if database is configured."""
        return bool(self.db_host and self.db_port)
```

### 3.3 API 클라이언트 작성

**파일**: `server/services/weather_client.py`

```python
# server/services/weather_client.py
"""Weather API client."""
import httpx
from typing import Dict, Any, Optional


class WeatherApiClient:
    """Client for weather API."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout_seconds: float = 10.0,
    ):
        """Initialize client.

        Args:
            base_url: Weather API base URL
            api_key: API authentication key
            timeout_seconds: Request timeout
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout_seconds
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }
            )
        return self._client

    async def get_weather(self, city: str) -> Dict[str, Any]:
        """Get weather information for a city.

        Args:
            city: City name

        Returns:
            Weather data dictionary

        Raises:
            httpx.HTTPError: On HTTP errors
            httpx.TimeoutException: On timeout
        """
        client = await self._get_client()

        url = f"{self.base_url}/weather"
        params = {"city": city}

        response = await client.get(url, params=params)
        response.raise_for_status()

        return response.json()

    async def close(self):
        """Close HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None
```

### 3.4 툴에서 API 클라이언트 사용

**파일**: `server/factory/server_factory.py`

```python
# server/factory/server_factory.py

elif tool.name == "get-weather":
    try:
        payload = GetWeatherInput.model_validate(arguments)
        city = payload.city

        # Weather API 클라이언트 생성
        weather_client = WeatherApiClient(
            base_url=cfg.weather_api_url,
            api_key=cfg.weather_api_key,
            timeout_seconds=30.0,
        )

        # API 호출
        weather_data = await weather_client.get_weather(city)
        await weather_client.close()

        # 위젯으로 반환
        widget = tools_by_name["weather-widget"].widget
        widget_resource = embedded_widget_resource(cfg, widget)

        return types.ServerResult(
            types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text=f"Weather for {city}"
                    )
                ],
                structuredContent={
                    "city": city,
                    "temperature": weather_data["temperature"],
                    "condition": weather_data["condition"],
                    "humidity": weather_data.get("humidity"),
                    "windSpeed": weather_data.get("wind_speed"),
                },
                _meta={
                    "openai.com/widget": widget_resource.model_dump(mode="json"),
                    **widget_tool_meta(widget),
                },
            )
        )

    except httpx.TimeoutException:
        return error_response("Weather API timeout")
    except httpx.HTTPError as e:
        return error_response(f"Weather API error: {e}")
```

---

## 4. 테스트하기

### 4.1 단위 테스트

**새 핸들러 테스트**:

```python
# server/tests/test_json_formatter.py
import pytest
from server.handlers.json_formatter import json_formatter_handler


def test_json_formatter_valid():
    """Test JSON formatter with valid input."""
    args = {
        "json_string": '{"name":"John","age":30}',
        "indent": 2
    }

    result = json_formatter_handler(args)

    assert "Formatted JSON:" in result
    assert '"name": "John"' in result
    assert '"age": 30' in result


def test_json_formatter_invalid():
    """Test JSON formatter with invalid input."""
    args = {
        "json_string": '{invalid json}',
    }

    result = json_formatter_handler(args)

    assert "Error: Invalid JSON" in result
```

**테스트 실행**:

```bash
pytest server/tests/test_json_formatter.py -v
```

### 4.2 통합 테스트

**파일**: `test_mcp.py` 수정

```python
# test_mcp.py

async def test_weather_widget_tool(mcp_server):
    """Test weather widget tool."""
    print("=" * 60)
    print("10. Testing Weather Widget Tool")
    print("=" * 60)

    request = types.CallToolRequest(
        params=types.CallToolRequestParams(
            name="weather-widget",
            arguments={
                "city": "Seoul",
                "temperature": 15.5,
                "condition": "Sunny",
                "humidity": 60,
                "windSpeed": 12
            }
        )
    )

    handler = mcp_server._mcp_server.request_handlers.get(types.CallToolRequest)
    result = await handler(request)

    content = result.content[0]
    assert content.type == "text"
    assert "structuredContent" in result.model_dump()

    structured = result.model_dump()["structuredContent"]
    assert structured["city"] == "Seoul"
    assert structured["temperature"] == 15.5

    print("\n✓ Weather widget test passed")
    print(f"  City: {structured['city']}")
    print(f"  Temperature: {structured['temperature']}°C")
    print(f"  Condition: {structured['condition']}\n")
```

### 4.3 ChatGPT 연결 테스트

#### Step 4.3.1: 서버 실행

```bash
npm run server
```

#### Step 4.3.2: ChatGPT Desktop 설정

**파일**: ChatGPT Desktop MCP 설정 (macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`)

```json
{
  "mcpServers": {
    "test-mcp-server": {
      "command": "python",
      "args": ["/path/to/test-mcp-server/server/main.py"],
      "env": {
        "EXTERNAL_API_BASE_URL": "https://api.yourservice.com",
        "EXTERNAL_API_KEY": "your-api-key"
      }
    }
  }
}
```

#### Step 4.3.3: ChatGPT에서 테스트

```
👤 "서울 날씨를 날씨 위젯으로 보여줘"

🤖 [weather-widget 툴 호출]

📊 [Weather Widget 렌더링]
   Seoul
   15°C ☀️
   Sunny
   Humidity: 60%
   Wind: 12 km/h
```

---

## 5. 배포 준비하기

### 5.1 환경 변수 체크리스트

**프로덕션 `.env` 파일**:

```bash
# .env (프로덕션)

# 서버 설정
HTTP_HOST=0.0.0.0
HTTP_PORT=8000
LOG_LEVEL=INFO

# 외부 API (필수)
EXTERNAL_API_BASE_URL=https://api.production.com
EXTERNAL_API_KEY=prod-api-key-xxxxxxxxxxxxx
EXTERNAL_API_TIMEOUT_S=30

# 날씨 API (선택)
WEATHER_API_URL=https://api.weather.com
WEATHER_API_KEY=weather-key-xxxxxxxxxxxxx

# 데이터베이스 (선택)
DB_HOST=prod-db.example.com
DB_PORT=5432
DB_NAME=myapp
DB_USER=dbuser
DB_PASSWORD=secure-password-here

# Assets 경로
ASSETS_DIR=components/assets

# CORS (필요시)
CORS_ALLOW_ORIGINS=*
```

**보안 주의사항**:
- ✅ `.env` 파일을 `.gitignore`에 추가
- ✅ API 키를 환경 변수나 시크릿 매니저에 저장
- ✅ 프로덕션과 개발 환경 분리

### 5.2 빌드 검증

```bash
# 1. 위젯 빌드
npm run build

# 예상 출력:
# ============================================================
# Build Summary
# ============================================================
# Widgets built: 3
#   - example
#   - api-result
#   - weather
# ============================================================
# ✅ All widget builds verified successfully!

# 2. 서버 테스트
python test_mcp.py

# 예상 출력:
# Testing Widget Loading: ✓
# Testing Tool Loading: ✓
# Testing Calculator: ✓
# Testing Weather Widget: ✓
# All tests passed!
```

### 5.3 프로덕션 체크리스트

#### 코드 체크리스트

- [ ] 모든 테스트 통과 (단위 + 통합)
- [ ] 빌드 검증 통과
- [ ] 에러 처리 구현 (모든 외부 API 호출)
- [ ] 로깅 적절히 설정 (INFO 레벨)
- [ ] 민감한 정보 하드코딩 제거

#### 환경 설정 체크리스트

- [ ] `.env` 파일 생성 (프로덕션 값)
- [ ] API 키 보안 확인
- [ ] CORS 설정 검토
- [ ] 타임아웃 설정 적절한지 확인

#### 위젯 체크리스트

- [ ] 모든 위젯 빌드 성공
- [ ] 위젯 HTML/JS/CSS 존재 확인
- [ ] 위젯 Props 검증 (Zod 스키마)
- [ ] 에러 폴백 구현

#### 툴 체크리스트

- [ ] 모든 툴 등록 확인 (`list_tools`)
- [ ] 툴 설명(description) 명확
- [ ] Input 스키마 정확
- [ ] 필수/선택 필드 명확

#### 배포 체크리스트

- [ ] 서버 정상 시작 확인
- [ ] ChatGPT에서 툴 목록 확인
- [ ] 각 툴 실행 테스트
- [ ] 에러 로그 모니터링 설정

### 5.4 서버 실행

**개발 환경**:
```bash
npm run server
# 또는
uvicorn server.main:app --reload --host 0.0.0.0 --port 8000
```

**프로덕션 환경**:
```bash
# Workers 추가 (멀티 프로세스)
uvicorn server.main:app --host 0.0.0.0 --port 8000 --workers 4

# 또는 Gunicorn + Uvicorn
gunicorn server.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### 5.5 모니터링

**로그 확인**:
```bash
# 서버 로그
tail -f server.log

# 예상 로그:
INFO     Starting Test MCP Server
INFO     Host: 0.0.0.0:8000
INFO     External API: ✓ Configured
INFO     Weather API: ✓ Configured
INFO     Registered tools: 5
  - calculator
  - external-fetch
  - json-formatter
  - weather-widget
  - get-weather
```

**헬스 체크**:
```bash
curl http://localhost:8000/health
# {"status": "ok"}
```

---

## 6. 예제 프로젝트 정리 상태

현재 프로젝트는 이미 정리가 완료된 상태입니다:

### 6.1 제거된 항목

✅ **api-result 위젯**: 완전히 제거됨
- `components/src/api-result/` 삭제
- `components/assets/api-result*` 삭제
- `server/services/widget_registry.py`에서 제거

✅ **calculator 툴**: 완전히 제거됨
- `server/handlers/calculator.py` 삭제
- `server/models/schemas.py`에서 CalculatorToolInput 삭제
- `server/services/tool_registry.py`에서 제거
- `server/factory/server_factory.py`에서 관련 코드 제거

### 6.2 유지된 항목

📌 **example 위젯**: 테스트용으로 코드만 유지
- 소스 코드: `components/src/example/` 유지
- 빌드 파일: `components/assets/example*` 유지
- 툴 등록: **Skip 처리** (MCP Inspector에 표시 안 됨)

### 6.3 현재 활성화된 툴

프로덕션 환경에서 사용 가능한 툴:

1. **get_games_by_sport** (TEXT)
   - 스포츠 경기 목록 조회
   - Input: `date`, `sport`

2. **get_game_details** (WIDGET)
   - 경기 상세 통계 표시
   - Input: `game_id`
   - Widget: `game-stats-widget`

### 6.4 실제 사용 예시

```bash
# 서버 실행
npm run server

# 등록된 툴 확인
# → 2개 툴만 표시됨 (get_games_by_sport, get_game_details)
```

---

## 7. 자주 묻는 질문 (FAQ)

### Q1: 위젯 Props 변경 시 주의사항?

**A**: Props 스키마 변경 시:
1. React 컴포넌트의 Zod 스키마 업데이트
2. 서버의 `structuredContent` 업데이트
3. 툴의 `input_schema` 업데이트
4. 재빌드: `npm run build`

### Q2: 여러 외부 API를 사용하려면?

**A**:
1. Config에 각 API 설정 추가
2. 각 API별 클라이언트 작성
3. `has_xxx_api` computed field 추가
4. 툴을 조건부로 등록

### Q3: 툴 실행이 느릴 때?

**A**:
- API 타임아웃 조정: `EXTERNAL_API_TIMEOUT_S=60`
- 비동기 처리 확인: `async/await` 사용
- 병렬 처리: `asyncio.gather()` 사용
- 캐싱 고려: Redis, in-memory cache

### Q4: 에러가 ChatGPT에 노출되지 않게 하려면?

**A**:
```python
try:
    # API 호출
    ...
except Exception as e:
    logger.error("Internal error: %s", e)  # 로그에만 상세 정보
    return error_response("Sorry, an error occurred")  # 사용자에게는 간단히
```

### Q5: 위젯 스타일이 깨질 때?

**A**:
1. Tailwind CSS 클래스 확인
2. `npm run build` 재실행
3. 브라우저 캐시 클리어
4. 빌드된 CSS 파일 확인: `components/assets/*.css`

---

## 8. 프로덕션 배포

### 8.1 개발 환경 vs 프로덕션 환경

#### 개발 환경 (현재 설정)

```bash
# MCP 서버
Host: 0.0.0.0:8000 (모든 네트워크 인터페이스)

# 컴포넌트 서버
Host: 127.0.0.1:4444 (로컬만)
BASE_URL: http://localhost:4444
```

**장점**:
- 간단한 설정
- 로컬 개발에 최적화
- 빠른 반복 개발

**제한사항**:
- ChatGPT/Claude 웹에서 사용 불가 (HTTPS → HTTP 차단)
- 외부 접근 불가

#### 프로덕션 환경

프로덕션에서는 **HTTPS**와 **공개 접근**이 필요합니다.

### 8.2 배포 옵션

#### 옵션 1: ngrok/Cloudflare Tunnel (빠른 테스트)

**장점**: 빠른 설정, 무료 티어 사용 가능
**단점**: 임시 URL, 성능 제한

**ngrok 사용:**

```bash
# 1. MCP 서버와 컴포넌트 서버를 ngrok으로 노출
cat > ~/ngrok.yml << 'EOF'
version: 2
authtoken: YOUR_NGROK_TOKEN
tunnels:
  mcp:
    proto: http
    addr: 8000
  components:
    proto: http
    addr: 4444
EOF

# 2. ngrok 실행
ngrok start --all --config ~/ngrok.yml

# 3. 출력된 URL 확인
# Forwarding  https://abc123.ngrok-free.dev -> http://localhost:8000
# Forwarding  https://def456.ngrok-free.dev -> http://localhost:4444

# 4. 컴포넌트를 ngrok URL로 재빌드
BASE_URL=https://def456.ngrok-free.dev npm run build

# 5. MCP 서버 재시작 (새 HTML 로드)
# 서버가 auto-reload이므로 자동으로 재시작됨
```

**Cloudflare Tunnel 사용:**

```bash
# 1. cloudflared 설치
# https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/

# 2. 터널 생성
cloudflared tunnel create mcp-server

# 3. config.yml 작성
cat > ~/.cloudflared/config.yml << 'EOF'
tunnel: YOUR_TUNNEL_ID
credentials-file: /home/june/.cloudflared/YOUR_TUNNEL_ID.json

ingress:
  - hostname: mcp.yourdomain.com
    service: http://localhost:8000
  - hostname: components.yourdomain.com
    service: http://localhost:4444
  - service: http_status:404
EOF

# 4. 터널 실행
cloudflared tunnel run
```

#### 옵션 2: VPS 배포 (안정적인 프로덕션)

**필요한 것**:
- VPS (AWS EC2, DigitalOcean, Linode 등)
- 도메인 이름
- SSL 인증서 (Let's Encrypt)

**배포 단계:**

```bash
# 1. VPS에 프로젝트 클론
git clone your-repo.git
cd test-mcp-server

# 2. 의존성 설치
npm run install:all

# 3. 환경 변수 설정
cp .env.example .env
# .env 파일 편집

# 4. 컴포넌트 빌드 (프로덕션 URL 사용)
BASE_URL=https://components.yourdomain.com npm run build

# 5. Nginx 리버스 프록시 설정
```

**Nginx 설정 예시:**

```nginx
# /etc/nginx/sites-available/mcp-server

# MCP 서버
server {
    listen 443 ssl http2;
    server_name mcp.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/mcp.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/mcp.yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;

        # SSE를 위한 설정
        proxy_buffering off;
        proxy_read_timeout 86400s;
    }
}

# 컴포넌트 서버
server {
    listen 443 ssl http2;
    server_name components.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/components.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/components.yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:4444;
        proxy_set_header Host $host;

        # CORS 설정
        add_header Access-Control-Allow-Origin *;
    }
}
```

**systemd 서비스 설정:**

```ini
# /etc/systemd/system/mcp-server.service
[Unit]
Description=MCP Server
After=network.target

[Service]
Type=simple
User=june
WorkingDirectory=/home/june/test-mcp-server
Environment="PATH=/home/june/test-mcp-server/.venv/bin"
ExecStart=/home/june/test-mcp-server/.venv/bin/uvicorn server.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```ini
# /etc/systemd/system/components-server.service
[Unit]
Description=Components Server
After=network.target

[Service]
Type=simple
User=june
WorkingDirectory=/home/june/test-mcp-server/components
ExecStart=/usr/bin/npx serve -s ./assets -p 4444 --cors
Restart=always

[Install]
WantedBy=multi-user.target
```

**서비스 시작:**

```bash
# 서비스 활성화
sudo systemctl enable mcp-server
sudo systemctl enable components-server

# 서비스 시작
sudo systemctl start mcp-server
sudo systemctl start components-server

# 상태 확인
sudo systemctl status mcp-server
sudo systemctl status components-server
```

#### 옵션 3: Docker 배포

**Dockerfile:**

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install Node.js
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Install dependencies
RUN pip install -r server/requirements.txt
RUN cd components && npm install && npm run build

# Expose ports
EXPOSE 8000

# Run server
CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml:**

```yaml
version: '3.8'

services:
  mcp-server:
    build: .
    ports:
      - "8000:8000"
    environment:
      - LOG_LEVEL=INFO
    restart: unless-stopped

  components-server:
    image: node:20-slim
    working_dir: /app/components
    volumes:
      - ./components:/app/components
    command: npx serve -s ./assets -p 4444 --cors
    ports:
      - "4444:4444"
    restart: unless-stopped
```

### 8.3 보안 고려사항

#### HTTPS 필수

**이유**:
- ChatGPT/Claude는 HTTPS만 지원
- Mixed Content 정책 (HTTPS → HTTP 차단)
- 데이터 암호화

#### CORS 설정

현재 설정 (`server/config.py`):
```python
cors_allow_origins: Tuple[str, ...] = Field(default=("*",))
```

**프로덕션에서는 특정 도메인만 허용:**
```python
cors_allow_origins: Tuple[str, ...] = Field(
    default=("https://chatgpt.com", "https://claude.ai")
)
```

#### API 키 보호

```bash
# .env 파일 사용
EXTERNAL_API_KEY=your-secret-key

# 환경 변수로 전달 (Docker)
docker run -e EXTERNAL_API_KEY=your-secret-key ...
```

### 8.4 모니터링 및 로깅

#### 로그 레벨 설정

```bash
# 프로덕션: INFO 또는 WARNING
LOG_LEVEL=WARNING

# 디버깅: DEBUG
LOG_LEVEL=DEBUG
```

#### 로그 수집

```python
# server/logging_config.py 확장
import logging.handlers

# 파일 로테이션
handler = logging.handlers.RotatingFileHandler(
    'logs/mcp-server.log',
    maxBytes=10485760,  # 10MB
    backupCount=5
)
```

### 8.5 성능 최적화

#### 캐싱

```python
# Redis 캐싱 예시
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(ttl=300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{args}:{kwargs}"
            cached = redis_client.get(key)
            if cached:
                return json.loads(cached)
            result = await func(*args, **kwargs)
            redis_client.setex(key, ttl, json.dumps(result))
            return result
        return wrapper
    return decorator
```

#### CDN 사용

컴포넌트 파일을 CDN에 호스팅:

```bash
# S3 + CloudFront
aws s3 sync components/assets s3://your-bucket/assets/
BASE_URL=https://cdn.yourdomain.com npm run build
```

### 8.6 체크리스트

프로덕션 배포 전 확인사항:

- [ ] HTTPS 설정 완료
- [ ] 환경 변수 설정 (`.env`)
- [ ] CORS 특정 도메인으로 제한
- [ ] API 키 보안 확인
- [ ] 로그 레벨 적절히 설정
- [ ] 컴포넌트를 프로덕션 URL로 빌드
- [ ] 서버 자동 재시작 설정 (systemd/Docker)
- [ ] 모니터링 설정
- [ ] 백업 전략 수립
- [ ] 방화벽 설정
- [ ] SSL 인증서 자동 갱신 (Let's Encrypt)

---

## 참조

- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - 설계 패턴 및 아키텍처
- **[REFACTORING_PLAN.md](./REFACTORING_PLAN.md)** - 리팩토링 계획
- **[README.md](./README.md)** - 프로젝트 개요
- **[.env.example](./.env.example)** - 환경 변수 예시

---

**마지막 업데이트**: 2025-11-23
**작성자**: Claude Code (with junho)

## 최근 업데이트 내역

### 2025-11-23
- ✅ Optional hashing 시스템 추가 (USE_HASH 환경 변수)
- ✅ 기본값 변경: 해시 사용 안 함 (더 간단한 배포)
- ✅ 위젯 로딩 상태 처리 베스트 프랙티스 추가
- ✅ 빌드 모드 가이드 (기본 vs 해시)
- ✅ window.openai.toolOutput 폴링 패턴 문서화
