import type { VolleyballGameData } from '../types';
import { Scoreboard, TeamComparison } from '../components';

interface BeforeGameProps {
  data: VolleyballGameData;
}

/**
 * 경기전 화면
 * - 양팀 비교 (팀 헤더 + 최근 5경기 + 맞대결 기록)
 * - 리그 순위
 */
export function BeforeGame({ data }: BeforeGameProps) {
  return (
    <div className="flex flex-col gap-4">
      <Scoreboard
        league={data.league}
        date={data.date}
        time={data.time}
        status={data.status}
        homeTeam={data.homeTeam}
        awayTeam={data.awayTeam}
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
