# Test MCP Server

MCP server with React widget support using FastMCP and OpenAI Apps SDK.

## Project Structure

```
test-mcp-server/
├── server/              # Python FastMCP server
│   ├── main.py         # MCP server entry point
│   ├── api_client.py   # External API HTTP client
│   ├── exceptions.py   # Custom exception classes
│   ├── test_api_client.py  # API client unit tests
│   └── requirements.txt
├── components/          # React UI components
│   ├── src/            # React source code
│   │   ├── example/    # Example widget
│   │   ├── api-result/ # API response visualization widget
│   │   └── index.css   # Shared styles
│   ├── assets/         # Built HTML/JS/CSS (generated)
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── build.ts        # Build script
├── test_mcp.py          # MCP server integration tests
├── package.json         # Root build scripts
├── .env.example         # Environment variables template
└── README.md
```

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

The server includes two built-in widgets:

### 1. Example Widget (`example`)
- **Purpose**: Demonstrates basic widget functionality
- **Props**: `message` (string)
- **Location**: `components/src/example/`
- **Usage**: Shows how to create a simple React widget with props

### 2. API Result Widget (`api-result`)
- **Purpose**: Visualizes external API responses
- **Props**: `success`, `endpoint`, `data`, `error`, `timestamp`
- **Location**: `components/src/api-result/`
- **Features**:
  - Success view with data summary and expandable JSON
  - Error view with detailed error information
  - Field badges and type indicators
  - Responsive design with Tailwind CSS

## Available Tools

The server provides three MCP tools:

### 1. Calculator (Text Tool)
- **Name**: `calculator`
- **Type**: Text-based tool
- **Input**: `expression` (string) - Math expression to evaluate
- **Output**: Calculated result or error message
- **Example**: `{"expression": "2 + 2"}` → `"Result: 4.0"`

### 2. Example Widget (Widget Tool)
- **Name**: `example-widget`
- **Type**: Widget-based tool
- **Input**: `message` (string, optional)
- **Output**: Renders the example widget with custom message
- **Widget**: Uses the Example Widget component

### 3. External Fetch (Dual-Mode Tool)
- **Name**: `external-fetch`
- **Type**: Widget or Text tool (configurable)
- **Input**:
  - `query` (string) - API endpoint path
  - `response_mode` (string) - "text" or "widget" (default: "text")
  - `params` (object, optional) - Query parameters
- **Output**:
  - Text mode: Formatted text with summary and JSON
  - Widget mode: Interactive API Result widget
- **Requirements**: `EXTERNAL_API_BASE_URL` and `EXTERNAL_API_KEY` environment variables

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
- Hash filenames for cache busting

### 3. Run the Server

```bash
npm run server
```

The MCP server will start on `http://0.0.0.0:8000`

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

Configure external API integration for the `external-fetch` tool:

```bash
EXTERNAL_API_BASE_URL=https://api.example.com
EXTERNAL_API_KEY=your-api-key-here
EXTERNAL_API_TIMEOUT_S=10.0           # Optional, default: 10.0
EXTERNAL_API_AUTH_HEADER=Authorization # Optional, default: Authorization
EXTERNAL_API_AUTH_SCHEME=Bearer        # Optional, default: Bearer
```

See [External API Integration](#external-api-integration) for more details.

## External API Integration

The server supports fetching data from external APIs with two response modes:

### Features

- **Text Mode**: Formatted text output with summary and full JSON
- **Widget Mode**: Interactive UI with data visualization
- **Error Handling**: Comprehensive error handling (timeout, HTTP errors, connection errors)
- **Authentication**: Configurable API key and authentication scheme

### Configuration

1. Create a `.env` file or set environment variables:

```bash
EXTERNAL_API_BASE_URL=https://jsonplaceholder.typicode.com
EXTERNAL_API_KEY=dummy
```

2. Start the server with environment variables:

```bash
env EXTERNAL_API_BASE_URL=https://api.example.com EXTERNAL_API_KEY=your-key npm run server
```

### Usage

#### Text Mode (Default)

Request formatted text output:

```python
# Via MCP tool call
{
  "name": "external-fetch",
  "arguments": {
    "query": "/posts/1",
    "response_mode": "text",
    "params": {"userId": 1}  # Optional query params
  }
}
```

Output:
```
✅ API Response Success
Endpoint: /posts/1

📊 Summary:
  - Keys: 4
  - Top-level fields: userId, id, title, body

📄 Full Response:
{...}
```

#### Widget Mode

Request interactive UI widget:

```python
# Via MCP tool call
{
  "name": "external-fetch",
  "arguments": {
    "query": "/posts/1",
    "response_mode": "widget"
  }
}
```

Returns an interactive widget with:
- Data summary and statistics
- Field preview with badges
- Expandable JSON view
- Error visualization (if request fails)

### Testing

Run integration tests with external API:

```bash
env EXTERNAL_API_BASE_URL=https://jsonplaceholder.typicode.com \
    EXTERNAL_API_KEY=dummy \
    .venv/bin/python test_mcp.py
```

The test suite includes:
- Text mode API fetch test
- Widget mode API fetch test
- Error handling verification

### API Client

The `ExternalApiClient` class provides:
- Async HTTP requests with `httpx`
- Configurable timeout and authentication
- Custom exception classes (`ApiTimeoutError`, `ApiHttpError`, `ApiConnectionError`)
- Automatic retry and error formatting

See `server/api_client.py` and `server/exceptions.py` for implementation details.

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
- ✅ Widget loading (2 widgets)
- ✅ Tool loading (3 tools)
- ✅ MCP protocol tools list
- ✅ MCP protocol resources list
- ✅ Widget tool execution (example-widget)
- ✅ Text tool execution (calculator)
- ✅ Resource reading (widget HTML)
- ✅ External API fetch - text mode
- ✅ External API fetch - widget mode

**Results**: 9/9 tests passing (14/14 total with unit tests)

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

## License

MIT
