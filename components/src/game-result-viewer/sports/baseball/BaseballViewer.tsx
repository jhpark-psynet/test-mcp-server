import type { BaseballGameData } from './types';
import { BeforeGame, LiveGame, AfterGame } from './views';

interface BaseballViewerProps {
  data: BaseballGameData;
}

export function BaseballViewer({ data }: BaseballViewerProps) {
  const { status } = data;

  return (
    <div className="w-full max-w-4xl mx-auto">
      {status === '예정' && <BeforeGame data={data} />}
      {status === '진행중' && <LiveGame data={data} />}
      {status === '종료' && <AfterGame data={data} />}
    </div>
  );
}

export default BaseballViewer;
