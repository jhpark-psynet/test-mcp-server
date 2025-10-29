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
