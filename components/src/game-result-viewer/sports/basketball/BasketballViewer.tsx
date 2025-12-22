import type { BasketballGameData } from './types';
import { BeforeGame, LiveGame, AfterGame } from './views';

interface BasketballViewerProps {
  data: BasketballGameData;
}

export function BasketballViewer({ data }: BasketballViewerProps) {
  const { status } = data;

  return (
    <div className="w-full max-w-4xl mx-auto">
      {status === '예정' && <BeforeGame data={data} />}
      {status === '진행중' && <LiveGame data={data} />}
      {status === '종료' && <AfterGame data={data} />}
    </div>
  );
}

export default BasketballViewer;
