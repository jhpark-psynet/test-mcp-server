import type { BasketballGameData } from '../types';
import { Scoreboard, PlayerStats, GameRecords, TeamComparison, LeagueStandings } from '../components';

interface AfterGameProps {
  data: BasketballGameData;
}

/**
 * 경기종료 화면
 * - 스코어보드 (최종 점수 + 쿼터별 점수)
 * - 선수 스탯 (탭)
 * - 경기 기록 (팀 스탯)
 * - 양팀 비교 (최근 5경기, 맞대결) - 서버 미제공으로 숨김
 * - 리그 순위
 */
export function AfterGame({ data }: AfterGameProps) {
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

      {/* 선수 스탯 */}
      {(data.homeTeam.players.length > 0 || data.awayTeam.players.length > 0) && (
        <PlayerStats
          homeTeam={data.homeTeam}
          awayTeam={data.awayTeam}
        />
      )}

      {/* 경기 기록 */}
      {data.gameRecords && data.gameRecords.length > 0 && (
        <GameRecords
          homeTeam={data.homeTeam}
          awayTeam={data.awayTeam}
          gameRecords={data.gameRecords}
        />
      )}

      {/* 양팀 비교 - 맞대결/최근경기 서버 미제공으로 임시 숨김 */}
      {/* <TeamComparison
        league={data.league}
        date={data.date}
        time={data.time}
        status={data.status}
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

export default AfterGame;
