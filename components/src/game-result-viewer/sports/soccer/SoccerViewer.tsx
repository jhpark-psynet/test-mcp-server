import type { SoccerGameData } from './types';
import { BeforeGame, LiveGame, AfterGame } from './views';

interface SoccerViewerProps {
  data: SoccerGameData;
}

export function SoccerViewer({ data }: SoccerViewerProps) {
  const { status } = data;

  return (
    <div className="w-full max-w-4xl mx-auto">
      {status === '경기전' && <BeforeGame data={data} />}
      {(status === '경기중' || status === '하프타임') && <LiveGame data={data} />}
      {status === '경기종료' && <AfterGame data={data} />}
    </div>
  );
}

export default SoccerViewer;
