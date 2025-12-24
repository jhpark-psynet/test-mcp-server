# Test MCP Server

MCP server with React widget support using FastMCP and OpenAI Apps SDK.

## Project Structure

```
test-mcp-server/
├── server/                      # Python FastMCP server (Modularized!)
│   ├── main.py                 # Entry point (32 lines!)
│   ├── config.py               # Configuration (Pydantic BaseSettings)
│   ├── logging_config.py       # Logging setup
│   ├── models/                 # Domain models
│   │   ├── widget.py          # Widget dataclass
│   │   ├── tool.py            # ToolDefinition (has_widget property)
│   │   └── schemas.py         # Pydantic schemas
│   ├── services/               # Business logic
│   │   ├── asset_loader.py    # HTML asset loading
│   │   ├── widget_registry.py # Widget registry
│   │   ├── tool_registry.py   # Tool registry
│   │   ├── response_formatter.py  # API formatters
│   │   ├── api_client.py      # ExternalApiClient (generic async)
│   │   ├── cache.py           # TTL cache for API responses
│   │   ├── exceptions.py      # Custom exceptions
│   │   └── sports/            # Modular Sports API (Phase 6)
│   │       ├── __init__.py    # SportsClientFactory
│   │       ├── base/          # Base classes
│   │       │   ├── client.py  # BaseSportsClient
│   │       │   └── mapper.py  # BaseResponseMapper
│   │       ├── basketball/    # Basketball module
│   │       ├── soccer/        # Soccer module
│   │       ├── volleyball/    # Volleyball module
│   │       └── football/      # Football module
│   ├── handlers/               # Tool handlers
│   │   └── sports.py          # Sports data handlers
│   ├── factory/                # MCP server factory
│   │   ├── safe_wrapper.py    # SafeFastMCPWrapper (Phase 2)
│   │   ├── server_factory.py  # MCP server creation
│   │   └── metadata_builder.py # OpenAI metadata
│   ├── main.py.backup          # Original (933 lines)
│   └── requirements.txt
├── components/                  # React UI components
│   ├── src/                    # React source code
│   │   ├── example/           # Example widget (테스트용)
│   │   ├── game-result-viewer/ # Game results viewer
│   │   └── index.css          # Shared styles
│   ├── assets/                 # Built HTML/JS/CSS (generated)
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── build.ts                # Build script
├── tests/                       # Test suite
│   └── test_cache.py           # Cache module tests (18 tests)
├── test_mcp.py                  # MCP integration tests
├── test_sports_api_integration.py  # Sports API integration tests
├── test_environment.py          # Environment configuration tests
├── package.json                 # Root build scripts
├── API_INTEGRATION.md          # API integration guide
├── REFACTORING_PLAN.md         # Refactoring plan (Phase 1-6 ✅)
└── README.md
```

**Recent Improvements** (Refactoring - Nov 2025):

**Phase 1** (Modularization):
- ✅ Modularized `main.py`: 933 → 32 lines (96.6% reduction)
- ✅ Layered architecture: models, services, handlers, factory
- ✅ 17 well-organized modules

**Phase 2** (Safety Wrapper):
- ✅ SafeFastMCPWrapper for FastMCP internal API protection
- ✅ Early detection of FastMCP API changes
- ✅ Clear error messages for debugging

**Phase 3** (Pydantic Settings):
- ✅ Config refactoring: dataclass → Pydantic BaseSettings
- ✅ Automatic environment variable validation
- ✅ .env file support with auto-loading
- ✅ Type safety with Field validators

**Phase 4** (Build Verification):
- ✅ Automated build verification script
- ✅ HTML/JS/CSS existence checks
- ✅ HTML reference validation

**Phase 5** (Sports MCP Implementation):
- ✅ Sports API integration (get_games_by_sport, get_game_details)
- ✅ Game Result Viewer widget with team/player statistics
- ✅ Multi-league support (NBA, KBL, WKBL, etc.)
- ✅ Clean tool architecture (2 production tools)

**Phase 6** (Sports API Modularization):
- ✅ Refactored Sports API into modular structure
- ✅ Factory pattern (SportsClientFactory)
- ✅ Base classes (BaseSportsClient, BaseResponseMapper)
- ✅ Sport-specific modules (basketball, soccer, volleyball, football)
- ✅ Improved readability and extensibility

**Phase 7** (TTL Cache Implementation):
- ✅ In-memory TTL cache for game list API responses
- ✅ Configurable TTL (default: 5 minutes) and max size (default: 100)
- ✅ Data validation before caching (required fields check)
- ✅ `force_refresh` parameter for cache bypass
- ✅ Cache hit/miss logging for debugging
- ✅ 18 unit tests for cache module

**Phase 8** (Multi-Sport Handler Refactoring):
- ✅ Refactored `get_game_details_handler` for all sports support
- ✅ Extended `BaseSportsClient` with optional methods (`get_lineup`, `get_team_rank`, `get_team_vs_list`)
- ✅ Extended `BaseResponseMapper` with `build_game_records()` abstract method
- ✅ Sport-specific `gameRecords` implementation (basketball, soccer, volleyball, football)
- ✅ Dynamic feature detection via `has_operation()` check
- ✅ Handler code reduction: 713 → 624 lines
- ✅ New sports can be added without modifying handler

## How It Works

1. **React Components** → Build to HTML/JS/CSS in `components/assets/`
2. **Python Server** reads HTML files from `assets/`
3. **MCP Resources** expose HTML as widgets
4. **ChatGPT Client** renders the widget with props from `structuredContent`

```
React (TSX) → Build → HTML → MCP Server → ChatGPT (Render)
                              ↓
                        structuredContent (props)
```

## Available Widgets

The server includes widgets for sports data visualization:

### 1. Example Widget (`example`) - Test Only
- **Purpose**: Demonstrates basic widget functionality (테스트용)
- **Props**: `message` (string)
- **Location**: `components/src/example/`
- **Status**: 테스트용으로 코드만 유지 (툴 목록에서 제외됨)

### 2. Game Result Viewer (`game-result-viewer`)
- **Purpose**: Displays detailed game statistics with team and player stats
- **Props**: `GameData` (league, date, status, homeTeam, awayTeam, gameRecords)
- **Location**: `components/src/game-result-viewer/`
- **Features**:
  - Game header with team scores and league info
  - Team statistics comparison table
  - Player statistics table (points, rebounds, assists, shooting %)
  - Zod schema validation
  - Responsive design with Tailwind CSS
- **Used by**: `get_game_details` tool

## Available Tools

The server provides sports data MCP tools:

### 1. Get Games by Sport (Text Tool)
- **Name**: `get_games_by_sport`
- **Type**: Text-based tool
- **Input**:
  - `date` (string) - Date in YYYYMMDD format (e.g., "20251118")
  - `sport` (string) - Sport type: basketball, soccer, volleyball, or football
  - `force_refresh` (boolean, optional) - Force refresh from API, ignoring cache
- **Output**: Formatted text with game schedules and results
- **Features**:
  - Lists games by league (NBA, KBL, WKBL, etc.)
  - Shows scores, time, arena, and game state
  - Includes game IDs for detailed queries
  - Team alias support (e.g., "Warriors" -> "Golden State")
  - **TTL Cache**: Results cached for 5 minutes to reduce API calls
- **Example**:
  ```json
  {"date": "20251118", "sport": "basketball"}
  ```
  Returns:
  ```
  ## Basketball Games on 20251118

  ### [NBA]
  - **클리블랜드** 118 - 106 **밀워키** (Finished, W)
    - Arena: 로킷 모기지 필드하우스
    - Game ID: `OT2025313104229`
  ```

### 2. Get Game Details (Widget Tool)
- **Name**: `get_game_details`
- **Type**: Widget-based tool
- **Input**:
  - `game_id` (string) - Game ID from get_games_by_sport result
- **Output**: Interactive widget with detailed game statistics
- **Widget**: Uses the Game Result Viewer component
- **Features**:
  - Game header with final scores
  - Team statistics (FG%, rebounds, assists, turnovers, etc.)
  - Player statistics (points, rebounds, assists, shooting %, etc.)
  - Sortable tables with responsive design
- **Supports all game states**:
  - Before game (state='s'): Team comparison, head-to-head records, standings
  - During game (state='p'): Live scores, current stats
  - After game (state='f'): Final scores, full player stats, game records
- **Example**:
  ```json
  {"game_id": "OT2025313104237"}
  ```

## Setup

### 1. Install Dependencies

```bash
# Install all dependencies (Python + Node)
npm run install:all

# Or install separately
npm run install:components  # Install React dependencies
npm run install:server      # Install Python dependencies
```

### 2. Build React Components

```bash
npm run build
```

This will:
- Build React components from `components/src/*/index.tsx`
- Generate HTML/JS/CSS in `components/assets/`

### 3. Environment Configuration

The server supports multiple environments (development, production) with separate configurations.

#### Development Environment (Default)

```bash
# The .env.development file is used automatically
npm run server        # or npm run server:dev
```

Settings:
- Uses **mock data** (no real API calls)
- Debug logging enabled
- Port 8000 (localhost)

#### Production Environment

```bash
# Create/edit .env.production file
vi .env.production

# Set required values:
# - SPORTS_API_KEY=your_actual_api_key
# - USE_MOCK_SPORTS_DATA=false
# - LOG_LEVEL=INFO

# Run in production mode
ENV=production npm run server:prod
# or
npm run start:prod
```

Settings:
- Uses **real API** calls
- Info logging
- Production-ready configuration

#### Environment Files

- `.env.development` - Development settings (auto-loaded, gitignored)
- `.env.production` - Production settings (create manually, gitignored)

**Important**: Never commit `.env.development` or `.env.production` to git!

### 4. Run the Server

```bash
# Development (default)
npm run server

# Development (explicit)
npm run server:dev

# Production
npm run server:prod
```

The MCP server will start on `http://0.0.0.0:8000`

## Build Process

```bash
npm run build
```

**What happens**:
1. Each widget in `components/src/*/index.tsx` is compiled
2. JS/CSS/HTML files are generated in `components/assets/`
3. Simple filenames like `example.js`, `example.css`

**Generated files**:
```
components/assets/
├── example.js
├── example.css
├── example.html
├── game-result-viewer.js
├── game-result-viewer.css
├── game-result-viewer.html
└── manifest.json
```

## Build Verification

The build process includes automatic verification to catch issues early:

```bash
# Build and verify (recommended)
npm run build

# Build without verification
npm run build:only

# Verify existing build
npm run build:verify
```

**What is verified**:
- ✅ HTML files exist for all widgets
- ✅ JS files exist for all widgets
- ✅ HTML references point to existing files
- ✅ No broken asset references

**Example output**:
```
Verifying widget builds...
============================================================
Widget: example
  HTML: ✅ example.html
  JS:   ✅ example.js
  CSS:  ✅ example.css

Widget: game-result-viewer
  HTML: ✅ game-result-viewer.html
  JS:   ✅ game-result-viewer.js
  CSS:  ✅ game-result-viewer.css

============================================================
✅ All widget builds verified successfully!

Verified 2 widget(s):
  - example
  - game-result-viewer
```

If verification fails, the build process will exit with an error and show what's missing. Fix the build and try again.

## Development Workflow

### Quick Start

```bash
npm run install:all  # First time only
npm run dev          # Build + Start server
```

### Watch Mode

```bash
# Terminal 1: Watch and rebuild on changes
npm run build:watch

# Terminal 2: Run server with auto-reload
npm run server
```

## Creating New Widgets

### 1. Create React Component

```bash
mkdir -p components/src/my-widget
```

Create `components/src/my-widget/index.tsx`:

```tsx
import { createRoot } from 'react-dom/client';

interface MyWidgetProps {
  data?: string;
}

function MyWidget({ data = "default" }: MyWidgetProps) {
  return (
    <div>
      <h1>My Widget</h1>
      <p>{data}</p>
    </div>
  );
}

const rootElement = document.getElementById('my-widget-root');
if (rootElement) {
  const root = createRoot(rootElement);
  root.render(<MyWidget />);
}

export default MyWidget;
```

### 2. Build

```bash
npm run build
```

This generates `components/assets/my-widget.html`

### 3. Register in Server

Edit `server/main.py`:

```python
widgets: List[Widget] = [
    Widget(
        identifier="my-widget",
        title="My Widget",
        template_uri="ui://widget/my-widget.html",
        invoking="Loading my widget",
        invoked="My widget loaded",
        html=_load_widget_html("my-widget"),
        response_text="Rendered my widget!",
    ),
]
```

### 4. Restart Server

```bash
npm run server
```

## Passing Props to React Components

Props are passed via `structuredContent` in the tool response:

```python
return types.ServerResult(
    types.CallToolResult(
        content=[...],
        structuredContent={"data": "Hello from MCP!"},  # ← Props
        _meta={
            "openai.com/widget": widget_resource.model_dump(mode="json"),
        }
    )
)
```

The React component receives these as props from ChatGPT's rendering engine.

## Static Asset Server

To serve assets independently (for testing):

```bash
cd components
npm run serve
```

Assets will be available at `http://localhost:4444`

## Environment Variables

### BASE_URL

Set the base URL for generated HTML asset references:

```bash
BASE_URL=http://your-domain.com:4444 npm run build
```

Default: `http://localhost:4444`

### External API Configuration

Configure external API integration:

```bash
EXTERNAL_API_BASE_URL=https://api.example.com
EXTERNAL_API_KEY=your-api-key-here
EXTERNAL_API_TIMEOUT_S=10.0           # Optional, default: 10.0
EXTERNAL_API_AUTH_HEADER=Authorization # Optional, default: Authorization
EXTERNAL_API_AUTH_SCHEME=Bearer        # Optional, default: Bearer
```

See [External API Integration](#external-api-integration) for more details.

## Sports API Integration

The server integrates with a sports data API to provide game schedules and detailed statistics:

### Features

- **Multi-league Support**: NBA, KBL, WKBL, and more
- **Game Schedules**: List games by date and sport
- **Detailed Statistics**: Team and player stats with interactive widgets
- **Real-time Data**: Fetch current game results and scores
- **Team Aliases**: Support for common team name variations

### Modular Architecture (Phase 6)

The Sports API uses a factory pattern with sport-specific clients:

```
SportsClientFactory.create_client("basketball")  # Returns BasketballClient
SportsClientFactory.create_client("soccer")      # Returns SoccerClient
SportsClientFactory.create_client("volleyball")  # Returns VolleyballClient
SportsClientFactory.create_client("football")    # Returns FootballClient
```

**Module Structure** (`server/services/sports/`):
- `__init__.py` - SportsClientFactory
- `base/client.py` - BaseSportsClient (abstract base class)
- `base/mapper.py` - BaseResponseMapper (field mapping)
- `basketball/` - Basketball-specific implementation
- `soccer/` - Soccer-specific implementation
- `volleyball/` - Volleyball-specific implementation
- `football/` - Football-specific implementation

**Features**:
- Mock data for development and testing
- Automatic fallback to mock when API not configured
- Structured data models for games, teams, and players
- Support for multiple leagues and sports
- Extensible architecture for new sports
- Sport-specific game records via `build_game_records()`

**Sport-specific Game Records**:
| Sport | Statistics |
|-------|------------|
| Basketball | 필드골, 3점슛, 자유투, 리바운드, 어시스트, 턴오버, 스틸, 블록, 파울 (9) |
| Soccer | 슈팅, 유효슈팅, 점유율, 패스, 패스성공률, 파울, 코너킥, 오프사이드 (8) |
| Volleyball | 공격 성공률, 블로킹, 서브 에이스, 서브 실패, 리시브 효율, 세트당 득점, 디그 (7) |
| Football | 총 야드, 패싱 야드, 러싱 야드, 1st 다운, 터노버, 소유 시간, 3rd 다운 성공률 (7) |

### Usage

#### Get Games by Sport

```python
# Via MCP tool call
{
  "name": "get_games_by_sport",
  "arguments": {
    "date": "20251118",
    "sport": "basketball"
  }
}
```

Returns formatted text with game list, scores, and game IDs.

#### Get Game Details

```python
# Via MCP tool call
{
  "name": "get_game_details",
  "arguments": {
    "game_id": "OT2025313104237"
  }
}
```

Returns an interactive widget with:
- Game header with team names and scores
- Team statistics table
- Player statistics table with detailed metrics
- Responsive design for different screen sizes

### Testing

Run sports tools tests:

```bash
.venv/bin/python test_sports_tools.py
```

The test suite includes:
- get_games_by_sport handler test
- get_game_details handler test
- Data structure validation

## Troubleshooting

### "Widget HTML not found"

Make sure you've built the React components:

```bash
npm run build
```

### Python dependencies not installed

```bash
source .venv/bin/activate  # Activate virtual environment
npm run install:server     # Install dependencies
```

### Port 8000 already in use

Edit `server/main.py` and change the port:

```python
uvicorn.run("main:app", host="0.0.0.0", port=8001)
```

## Testing

The project includes comprehensive test coverage:

### Unit Tests

Test the API client in isolation:

```bash
# Activate virtual environment
source .venv/bin/activate

# Run API client unit tests
pytest server/test_api_client.py -v
```

**Test Coverage** (`server/test_api_client.py`):
- ✅ Successful API requests
- ✅ HTTP error handling (404, 500)
- ✅ Timeout handling
- ✅ Connection error handling
- ✅ Query parameter encoding

**Results**: 5/5 tests passing

### Integration Tests

Test the complete MCP server:

```bash
# Run MCP server integration tests
.venv/bin/python test_mcp.py

# With external API (optional)
env EXTERNAL_API_BASE_URL=https://jsonplaceholder.typicode.com \
    EXTERNAL_API_KEY=dummy \
    .venv/bin/python test_mcp.py
```

**Test Coverage** (`test_mcp.py`):
- ✅ Widget loading
- ✅ Tool loading (2 sports tools)
- ✅ MCP protocol tools list
- ✅ MCP protocol resources list
- ✅ Widget tool execution (get_game_details)
- ✅ Text tool execution (get_games_by_sport)
- ✅ Resource reading (widget HTML)

**Results**: Tests passing for sports functionality

**Sports Tools Tests** (`test_sports_tools.py`):
- ✅ get_games_by_sport handler
- ✅ get_game_details handler
- ✅ Data validation

**Results**: 2/2 tests passing

## Tech Stack

### Backend
- **FastMCP 2.0**: MCP server framework
- **httpx**: Async HTTP client for external API calls
- **Uvicorn**: ASGI web server
- **Starlette**: Web framework
- **pytest**: Testing framework with async support

### Frontend
- **React 19**: UI component library
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS 4.1**: Utility-first CSS framework
- **Zod**: Runtime type validation

### Build Tools
- **Vite 7**: Fast build tool and dev server
- **esbuild**: JavaScript bundler
- **npm**: Package manager

### Protocol
- **MCP (Model Context Protocol)**: Communication protocol between LLM clients and servers

## Documentation

### Getting Started
- **[CUSTOMIZATION_GUIDE.md](./CUSTOMIZATION_GUIDE.md)** - 실제 프로젝트에 적용하기 ⭐ **필독!**
  - 새로운 위젯 추가하기 (Weather Widget 예제)
  - 새로운 툴 추가하기 (단순/복잡 툴)
  - 외부 API 통합하기
  - 테스트 및 배포 준비
  - 예제 프로젝트 제거

### Architecture & Design Patterns
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - 핵심 설계 패턴 및 아키텍처 결정 사항
  - SafeFastMCPWrapper 패턴: FastMCP 내부 API 안전 래핑
  - External API 툴 관리: 동적 툴 등록 구조
  - 레이어드 아키텍처: 관심사 분리

### Planning & Progress
- **[REFACTORING_PLAN.md](./REFACTORING_PLAN.md)** - 전체 리팩토링 계획 및 Phase 1-5 완료 보고서
- **[IMPROVEMENT_RECOMMENDATIONS.md](./IMPROVEMENT_RECOMMENDATIONS.md)** - 개선 제안 및 완료 상태 (6/6 완료)

### Technical Documentation
- **[claude.md](./claude.md)** - 상세 기술 문서 및 사용법
- **[API_INTEGRATION.md](./API_INTEGRATION.md)** - API 통합 가이드

## Deployment

### Cloudflare Tunnel

The server can be exposed to the internet using Cloudflare Tunnel:

```bash
# Install cloudflared
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb -o /tmp/cloudflared.deb
sudo dpkg -i /tmp/cloudflared.deb

# Login and create tunnel
cloudflared tunnel login
cloudflared tunnel create mcpapps

# Configure tunnel (/etc/cloudflared/config.yml)
tunnel: <UUID>
credentials-file: /etc/cloudflared/<UUID>.json

ingress:
  - hostname: mcpapps.yourdomain.com
    service: http://localhost:8000
  - service: http_status:404

# Route DNS and start
cloudflared tunnel route dns mcpapps mcpapps.yourdomain.com
sudo cloudflared service install
sudo systemctl start cloudflared
```

**Production URL**: `https://mcpapps.selfwell.kr/mcp`

## License

MIT
