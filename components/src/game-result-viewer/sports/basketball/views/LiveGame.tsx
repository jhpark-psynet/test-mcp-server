import type { BasketballGameData } from '../types';
import { Scoreboard, GameRecords, TeamComparison, LeagueStandings } from '../components';

interface LiveGameProps {
  data: BasketballGameData;
}

/**
 * 경기중 화면
 * - 스코어보드 (현재 점수 + 쿼터별 점수)
 * - 경기 기록 (팀 스탯)
 * - 양팀 비교 (최근 5경기, 맞대결) - 서버 미제공으로 숨김
 * - 리그 순위
 */
export function LiveGame({ data }: LiveGameProps) {
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

      {/* 경기 기록 */}
      {data.gameRecords && data.gameRecords.length > 0 && (
        <GameRecords
          homeTeam={data.homeTeam}
          awayTeam={data.awayTeam}
          gameRecords={data.gameRecords}
        />
      )}

      {/* 양팀 비교 (최근 5경기 + 시즌 통계) */}
      <TeamComparison
        homeTeam={data.homeTeam}
        awayTeam={data.awayTeam}
        teamComparison={data.teamComparison}
      />

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

export default LiveGame;
