import { createRoot } from 'react-dom/client';
import { z } from 'zod';
import { useState } from 'react';
import '../index.css';

// Zod schema for props validation
const ApiResultPropsSchema = z.object({
  success: z.boolean(),
  endpoint: z.string(),
  data: z.any().optional(),
  error: z.object({
    type: z.string(),
    message: z.string(),
    details: z.string().optional(),
  }).optional(),
  timestamp: z.string().optional(),
});

type ApiResultProps = z.infer<typeof ApiResultPropsSchema>;

function SuccessView({ endpoint, data, timestamp }: { endpoint: string; data: any; timestamp?: string }) {
  const [showRaw, setShowRaw] = useState(false);

  // Extract summary info
  const getSummary = () => {
    if (Array.isArray(data)) {
      return {
        type: 'Array',
        count: data.length,
        preview: data.slice(0, 3),
      };
    } else if (typeof data === 'object' && data !== null) {
      return {
        type: 'Object',
        keys: Object.keys(data).length,
        topKeys: Object.keys(data).slice(0, 5),
      };
    } else {
      return {
        type: typeof data,
        value: String(data),
      };
    }
  };

  const summary = getSummary();

  return (
    <div className="max-w-4xl mx-auto my-8 p-6 bg-white rounded-lg shadow-lg">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6 pb-4 border-b border-gray-200">
        <div className="flex-shrink-0 w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
          <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-gray-800">API Response Success</h1>
          <p className="text-sm text-gray-600 font-mono mt-1">{endpoint}</p>
        </div>
        {timestamp && (
          <div className="text-xs text-gray-500">
            {new Date(timestamp).toLocaleString()}
          </div>
        )}
      </div>

      {/* Summary Section */}
      <div className="mb-6 p-4 bg-blue-50 rounded-lg">
        <h2 className="text-lg font-semibold text-blue-900 mb-3">📊 Summary</h2>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <span className="text-sm text-blue-700 font-medium">Type:</span>
            <span className="ml-2 text-sm text-blue-900">{summary.type}</span>
          </div>
          {summary.type === 'Array' && (
            <div>
              <span className="text-sm text-blue-700 font-medium">Items:</span>
              <span className="ml-2 text-sm text-blue-900">{summary.count}</span>
            </div>
          )}
          {summary.type === 'Object' && (
            <>
              <div>
                <span className="text-sm text-blue-700 font-medium">Keys:</span>
                <span className="ml-2 text-sm text-blue-900">{summary.keys}</span>
              </div>
              <div className="col-span-2">
                <span className="text-sm text-blue-700 font-medium">Fields:</span>
                <div className="mt-1 flex flex-wrap gap-2">
                  {summary.topKeys.map((key: string) => (
                    <span key={key} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                      {key}
                    </span>
                  ))}
                </div>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Data Preview */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-semibold text-gray-800">📄 Response Data</h2>
          <button
            onClick={() => setShowRaw(!showRaw)}
            className="px-3 py-1 text-sm bg-gray-200 hover:bg-gray-300 text-gray-800 rounded transition-colors"
          >
            {showRaw ? 'Show Preview' : 'Show Raw JSON'}
          </button>
        </div>

        {showRaw ? (
          <pre className="p-4 bg-gray-900 text-green-400 rounded-lg overflow-auto max-h-96 text-sm font-mono">
            {JSON.stringify(data, null, 2)}
          </pre>
        ) : (
          <div className="p-4 bg-gray-50 rounded-lg">
            {summary.type === 'Array' && Array.isArray(data) && (
              <div className="space-y-2">
                {data.slice(0, 5).map((item: any, idx: number) => (
                  <div key={idx} className="p-3 bg-white rounded border border-gray-200">
                    <div className="text-xs text-gray-500 mb-1">Item {idx + 1}</div>
                    <pre className="text-sm text-gray-800 overflow-auto">
                      {JSON.stringify(item, null, 2)}
                    </pre>
                  </div>
                ))}
                {data.length > 5 && (
                  <div className="text-sm text-gray-600 text-center py-2">
                    ... and {data.length - 5} more items
                  </div>
                )}
              </div>
            )}
            {summary.type === 'Object' && (
              <pre className="text-sm text-gray-800 overflow-auto">
                {JSON.stringify(data, null, 2)}
              </pre>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function ErrorView({ endpoint, error, timestamp }: { endpoint: string; error: any; timestamp?: string }) {
  const getErrorIcon = () => {
    if (error.type?.includes('Timeout')) return '🕐';
    if (error.type?.includes('HTTP')) return '🚫';
    if (error.type?.includes('Connection')) return '🔌';
    return '⚠️';
  };

  const getErrorColor = () => {
    if (error.type?.includes('Timeout')) return 'yellow';
    if (error.type?.includes('HTTP')) return 'red';
    if (error.type?.includes('Connection')) return 'orange';
    return 'red';
  };

  const color = getErrorColor();
  const bgColor = `bg-${color}-50`;
  const textColor = `text-${color}-900`;
  const borderColor = `border-${color}-200`;

  return (
    <div className="max-w-4xl mx-auto my-8 p-6 bg-white rounded-lg shadow-lg">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6 pb-4 border-b border-red-200">
        <div className="flex-shrink-0 w-12 h-12 bg-red-100 rounded-full flex items-center justify-center text-2xl">
          {getErrorIcon()}
        </div>
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-red-800">API Request Failed</h1>
          <p className="text-sm text-gray-600 font-mono mt-1">{endpoint}</p>
        </div>
        {timestamp && (
          <div className="text-xs text-gray-500">
            {new Date(timestamp).toLocaleString()}
          </div>
        )}
      </div>

      {/* Error Details */}
      <div className="space-y-4">
        <div className="p-4 bg-red-50 rounded-lg border border-red-200">
          <h2 className="text-lg font-semibold text-red-900 mb-2">Error Type</h2>
          <p className="text-red-800 font-mono">{error.type || 'Unknown Error'}</p>
        </div>

        <div className="p-4 bg-red-50 rounded-lg border border-red-200">
          <h2 className="text-lg font-semibold text-red-900 mb-2">Message</h2>
          <p className="text-red-800">{error.message || 'No error message provided'}</p>
        </div>

        {error.details && (
          <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900 mb-2">Details</h2>
            <pre className="text-sm text-gray-800 overflow-auto whitespace-pre-wrap">
              {error.details}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}

function App(props: ApiResultProps) {
  if (props.success && props.data !== undefined) {
    return <SuccessView endpoint={props.endpoint} data={props.data} timestamp={props.timestamp} />;
  } else if (!props.success && props.error) {
    return <ErrorView endpoint={props.endpoint} error={props.error} timestamp={props.timestamp} />;
  } else {
    return (
      <div className="max-w-4xl mx-auto my-8 p-6 bg-white rounded-lg shadow-lg">
        <div className="text-center text-gray-600">
          Invalid props: missing data or error
        </div>
      </div>
    );
  }
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
const rootElement = document.getElementById('api-result-root');
if (rootElement) {
  const root = createRoot(rootElement);

  // In a real scenario, props would come from the MCP server via structuredContent
  // For now, we'll use default props for development
  const externalProps = {
    success: true,
    endpoint: '/api/example',
    data: {
      id: 1,
      title: 'Example Data',
      count: 42,
    },
    timestamp: new Date().toISOString(),
  };

  // Validate props with Zod
  try {
    const validatedProps = ApiResultPropsSchema.parse(externalProps);
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
