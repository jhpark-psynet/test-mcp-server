import type { BaseballGameData } from '../types';
import { Scoreboard, PlayerStats, GameRecords } from '../components';

interface LiveGameProps {
  data: BaseballGameData;
}

export function LiveGame({ data }: LiveGameProps) {
  return (
    <div className="flex flex-col gap-4">
      <Scoreboard
        league={data.league}
        date={data.date}
        time={data.time}
        status={data.status}
        venue={data.venue}
        homeTeam={data.homeTeam}
        awayTeam={data.awayTeam}
        homeStarterName={data.homeStarterName}
        awayStarterName={data.awayStarterName}
      />
      {data.gameRecords && data.gameRecords.length > 0 && (
        <GameRecords
          homeTeam={data.homeTeam}
          awayTeam={data.awayTeam}
          gameRecords={data.gameRecords}
        />
      )}
      <PlayerStats
        homeTeam={data.homeTeam}
        awayTeam={data.awayTeam}
      />
    </div>
  );
}

export default LiveGame;
