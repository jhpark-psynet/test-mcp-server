import { createRoot } from 'react-dom/client';
import { z } from 'zod';
import '../index.css';

// Zod schema for props validation
const AppPropsSchema = z.object({
  message: z.string().default("Hello from React!"),
  timestamp: z.string().datetime().optional(),
  metadata: z.object({
    source: z.string().optional(),
    version: z.string().optional(),
  }).optional(),
});

type AppProps = z.infer<typeof AppPropsSchema>;

function App({ message, timestamp, metadata }: AppProps) {
  return (
    <div className="max-w-2xl mx-auto my-8 p-8 bg-gray-50 rounded-lg shadow-lg">
      <h1 className="text-3xl font-bold text-gray-800 mb-4">Example Widget</h1>

      <p className="text-xl text-blue-600 mb-6 p-4 bg-white rounded border-l-4 border-blue-600">
        {message}
      </p>

      <div className="p-4 bg-white rounded space-y-2">
        <p className="text-gray-600 leading-relaxed">
          This is a React component rendered via MCP server.
        </p>
        <p className="text-gray-600 leading-relaxed">
          Props are passed through{' '}
          <code className="bg-gray-100 px-2 py-1 rounded text-pink-600 font-mono text-sm">
            structuredContent
          </code>
          {' '}and validated with{' '}
          <code className="bg-gray-100 px-2 py-1 rounded text-pink-600 font-mono text-sm">
            Zod
          </code>.
        </p>

        {timestamp && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <p className="text-sm text-gray-500">
              Timestamp: {new Date(timestamp).toLocaleString()}
            </p>
          </div>
        )}

        {metadata && (
          <div className="mt-2 text-sm text-gray-500">
            {metadata.source && <p>Source: {metadata.source}</p>}
            {metadata.version && <p>Version: {metadata.version}</p>}
          </div>
        )}
      </div>
    </div>
  );
}

function ErrorFallback({ error }: { error: string }) {
  return (
    <div className="max-w-2xl mx-auto my-8 p-8 bg-red-50 rounded-lg shadow-lg border-2 border-red-200">
      <h1 className="text-2xl font-bold text-red-800 mb-4">Validation Error</h1>
      <p className="text-red-600 font-mono text-sm whitespace-pre-wrap">{error}</p>
    </div>
  );
}

// Initialize the app
const rootElement = document.getElementById('example-root');
if (rootElement) {
  const root = createRoot(rootElement);

  // In a real scenario, props would come from the MCP server
  // via structuredContent. For now, we'll use default props.
  const externalProps = {
    message: "Hello from MCP Server!",
    timestamp: new Date().toISOString(),
    metadata: {
      source: "MCP Server",
      version: "1.0.0",
    }
  };

  // Validate props with Zod
  try {
    const validatedProps = AppPropsSchema.parse(externalProps);
    root.render(<App {...validatedProps} />);
  } catch (error) {
    if (error instanceof z.ZodError) {
      const errorMessage = error.errors
        .map(err => `${err.path.join('.')}: ${err.message}`)
        .join('\n');
      root.render(<ErrorFallback error={errorMessage} />);
    } else {
      root.render(<ErrorFallback error="Unknown error occurred" />);
    }
  }
}

export default App;
