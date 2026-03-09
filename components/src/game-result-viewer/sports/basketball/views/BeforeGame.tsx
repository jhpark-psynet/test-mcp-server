import type { BasketballGameData } from '../types';
import { Scoreboard, TeamComparison } from '../components';

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

      {/* 양팀 비교 (최근 5경기 + 시즌 통계) */}
      <TeamComparison
        homeTeam={data.homeTeam}
        awayTeam={data.awayTeam}
        teamComparison={data.teamComparison}
        headToHead={data.headToHead}
      />

    </div>
  );
}

export default BeforeGame;
