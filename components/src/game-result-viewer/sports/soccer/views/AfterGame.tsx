import type { SoccerGameData } from '../types';
import { Scoreboard, GoalTimeline, PlayerStats, GameRecords, TeamComparison, LeagueStandings } from '../components';

interface AfterGameProps {
  data: SoccerGameData;
}

/**
 * 경기종료 화면
 * - 스코어보드 (최종 점수 + 전/후반 점수)
 * - 골 타임라인
 * - 선수 스탯 (탭)
 * - 경기 기록 (팀 스탯)
 * - 양팀 비교 (최근 5경기, 맞대결)
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
        homeTeam={data.homeTeam}
        awayTeam={data.awayTeam}
      />

      {/* 골 타임라인 */}
      {data.goals && data.goals.length > 0 && (
        <GoalTimeline
          goals={data.goals}
          homeTeam={data.homeTeam}
          awayTeam={data.awayTeam}
        />
      )}

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

export default AfterGame;
