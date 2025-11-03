# Test MCP Server

MCP server with React widget support using FastMCP and OpenAI Apps SDK.

## Project Structure

```
test-mcp-server/
├── server/              # Python FastMCP server
│   ├── main.py         # MCP server entry point
│   └── requirements.txt
├── components/          # React UI components
│   ├── src/            # React source code
│   │   └── example/    # Example widget
│   ├── assets/         # Built HTML/JS/CSS (generated)
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── build.ts        # Build script
├── package.json         # Root build scripts
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

## Tech Stack

- **Python**: FastMCP 2.0, Uvicorn, Starlette
- **React**: React 19, TypeScript
- **Build**: Vite, esbuild
- **MCP**: Model Context Protocol

## License

MIT
