import type { BasketballGameData } from '../types';
import { Scoreboard, TeamComparison, LeagueStandings } from '../components';

interface BeforeGameProps {
  data: BasketballGameData;
}

/**
 * 경기전 화면
 * - 스코어보드 (경기 정보)
 * - 양팀 비교 (팀 헤더 + 최근 5경기 + 맞대결 기록)
 * - 리그 순위
 */
export function BeforeGame({ data }: BeforeGameProps) {
  return (
    <div className="flex flex-col gap-4">
      {/* 스코어보드 */}
      <Scoreboard
        league={data.league}
        date={data.date}
        time={data.time}
        status={data.status}
        venue={data.venue}
        homeTeam={data.homeTeam}
        awayTeam={data.awayTeam}
      />

      {/* 양팀 비교 - 맞대결/최근경기 서버 미제공으로 임시 숨김 */}
      {/* <TeamComparison
        league={data.league}
        date={data.date}
        time={data.time}
        status={data.status}
        venue={data.venue}
        homeTeam={data.homeTeam}
        awayTeam={data.awayTeam}
        headToHead={data.headToHead}
      /> */}

      {/* 리그 순위 */}
      {data.standings && data.standings.length > 0 && (
        <LeagueStandings
          standings={data.standings}
          homeTeamName={data.homeTeam.shortName}
          awayTeamName={data.awayTeam.shortName}
        />
      )}
    </div>
  );
}

export default BeforeGame;
