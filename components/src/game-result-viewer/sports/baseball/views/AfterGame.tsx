import type { BaseballGameData } from '../types';
import { Scoreboard, PlayerStats, GameRecords, TeamComparison } from '../components';

interface AfterGameProps {
  data: BaseballGameData;
}

export function AfterGame({ data }: AfterGameProps) {
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
      <PlayerStats
        homeTeam={data.homeTeam}
        awayTeam={data.awayTeam}
      />
      {data.gameRecords && data.gameRecords.length > 0 && (
        <GameRecords
          homeTeam={data.homeTeam}
          awayTeam={data.awayTeam}
          gameRecords={data.gameRecords}
        />
      )}
      <TeamComparison
        homeTeam={data.homeTeam}
        awayTeam={data.awayTeam}
        headToHead={data.headToHead}
      />
    </div>
  );
}

export default AfterGame;
