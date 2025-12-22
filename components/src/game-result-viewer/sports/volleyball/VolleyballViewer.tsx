import type { VolleyballGameData } from './types';
import { BeforeGame, LiveGame, AfterGame } from './views';

interface VolleyballViewerProps {
  data: VolleyballGameData;
}

export function VolleyballViewer({ data }: VolleyballViewerProps) {
  const { status } = data;

  return (
    <div className="w-full max-w-4xl mx-auto">
      {status === '경기전' && <BeforeGame data={data} />}
      {status === '경기중' && <LiveGame data={data} />}
      {status === '경기종료' && <AfterGame data={data} />}
    </div>
  );
}

export default VolleyballViewer;
