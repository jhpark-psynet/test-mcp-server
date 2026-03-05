import type { VolleyballGameData } from './types';
import { BeforeGame, LiveGame, AfterGame } from './views';

interface VolleyballViewerProps {
  data: VolleyballGameData;
}

export function VolleyballViewer({ data }: VolleyballViewerProps) {
  const { status } = data;

  return (
    <div className="w-full max-w-4xl mx-auto">
      {status === '예정' && <BeforeGame data={data} />}
      {status === '진행중' && <LiveGame data={data} />}
      {status === '종료' && <AfterGame data={data} />}
    </div>
  );
}

export default VolleyballViewer;
