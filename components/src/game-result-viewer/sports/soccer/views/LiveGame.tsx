import type { SoccerGameData } from '../types';
import { Scoreboard, GoalTimeline, GameRecords, TeamComparison, LeagueStandings } from '../components';

interface LiveGameProps {
  data: SoccerGameData;
}

/**
 * 경기중 화면
 * - 스코어보드 (현재 점수 + 전/후반 점수)
 * - 골 타임라인
 * - 경기 기록 (팀 스탯)
 * - 양팀 비교 (최근 5경기, 맞대결)
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
        currentPeriod={data.currentPeriod}
        currentMinute={data.currentMinute}
        addedTime={data.addedTime}
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

export default LiveGame;
