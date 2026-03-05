import type { BaseballGameData } from '../types';
import { Scoreboard, TeamComparison } from '../components';

interface BeforeGameProps {
  data: BaseballGameData;
}

export function BeforeGame({ data }: BeforeGameProps) {
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
      <TeamComparison
        homeTeam={data.homeTeam}
        awayTeam={data.awayTeam}
        headToHead={data.headToHead}
      />
    </div>
  );
}

export default BeforeGame;
