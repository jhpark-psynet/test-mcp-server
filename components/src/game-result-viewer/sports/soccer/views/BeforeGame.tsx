import type { SoccerGameData } from '../types';
import { Scoreboard, TeamComparison } from '../components';

interface BeforeGameProps {
  data: SoccerGameData;
}

/**
 * 경기전 화면
 * - 스코어보드 (리그명, 날짜, 시간, 예정 뱃지)
 * - 양팀 비교 (팀 헤더 + 최근 5경기 + 맞대결 기록)
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

      {/* 양팀 비교 */}
      <TeamComparison
        homeTeam={data.homeTeam}
        awayTeam={data.awayTeam}
        headToHead={data.headToHead}
      />
    </div>
  );
}

export default BeforeGame;
