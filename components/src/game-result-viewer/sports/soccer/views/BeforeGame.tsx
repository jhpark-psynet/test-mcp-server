import type { SoccerGameData } from '../types';
import { TeamComparison, LeagueStandings } from '../components';

interface BeforeGameProps {
  data: SoccerGameData;
}

/**
 * 경기전 화면
 * - 양팀 비교 (팀 헤더 + 최근 5경기 + 맞대결 기록)
 * - 리그 순위
 */
export function BeforeGame({ data }: BeforeGameProps) {
  return (
    <div className="flex flex-col gap-4">
      {/* 양팀 비교 */}
      <TeamComparison
        league={data.league}
        date={data.date}
        time={data.time}
        status={data.status}
        homeTeam={data.homeTeam}
        awayTeam={data.awayTeam}
        headToHead={data.headToHead}
      />

      {/* 리그 순위 */}
      {data.standings && data.standings.length > 0 && (
        <LeagueStandings
          standings={data.standings}
          homeTeam={data.homeTeam}
          awayTeam={data.awayTeam}
        />
      )}
    </div>
  );
}

export default BeforeGame;
