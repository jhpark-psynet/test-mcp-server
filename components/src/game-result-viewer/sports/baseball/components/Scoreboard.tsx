import type { BaseballTeamInfo, GameStatus } from '../types';

interface ScoreboardProps {
  league: string;
  date: string;
  time?: string;
  status: GameStatus;
  venue?: string;
  homeTeam: BaseballTeamInfo;
  awayTeam: BaseballTeamInfo;
  homeStarterName?: string;
  awayStarterName?: string;
}

export function Scoreboard({
  league, date, time, status, venue, homeTeam, awayTeam,
  homeStarterName, awayStarterName,
}: ScoreboardProps) {
  const hasInnings = homeTeam.inningScores && homeTeam.inningScores.length > 0;

  const getStatusColor = (s: GameStatus) => {
    switch (s) {
      case '종료': return 'text-gray-500';
      case '진행중': return 'text-red-600';
      case '예정': return 'text-blue-600';
    }
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200">
      {/* 헤더 */}
      <div className="flex justify-between items-center px-3 py-1.5 border-b border-gray-100">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-sm text-blue-600">{league}</span>
          <span className="text-gray-600 text-sm">{date}</span>
          {time && status === '예정' && (
            <span className="text-gray-700 text-sm">{time}</span>
          )}
          {venue && <span className="text-gray-400 text-xs">{venue}</span>}
        </div>
        <span className={`text-sm font-semibold ${getStatusColor(status)}`}>
          {status}
        </span>
      </div>

      {/* 스코어 영역 */}
      <div className="flex items-center justify-center py-3 px-2 gap-4">
        {/* 원정팀 */}
        <div className="flex flex-col items-center gap-1 flex-1">
          <TeamLogo team={awayTeam} />
          <div className="text-center">
            <div className="font-semibold text-sm text-gray-800">{awayTeam.shortName}</div>
            {awayTeam.record && <div className="text-xs text-gray-500">{awayTeam.record}</div>}
          </div>
        </div>

        {/* 점수 */}
        <div className="flex items-center gap-3">
          <span className="text-3xl font-bold text-gray-900 tabular-nums w-8 text-center">
            {status === '예정' ? '-' : awayTeam.score}
          </span>
          <span className="text-lg text-gray-400">:</span>
          <span className="text-3xl font-bold text-gray-900 tabular-nums w-8 text-center">
            {status === '예정' ? '-' : homeTeam.score}
          </span>
        </div>

        {/* 홈팀 */}
        <div className="flex flex-col items-center gap-1 flex-1">
          <TeamLogo team={homeTeam} />
          <div className="text-center">
            <div className="font-semibold text-sm text-gray-800">{homeTeam.shortName}</div>
            {homeTeam.record && <div className="text-xs text-gray-500">{homeTeam.record}</div>}
          </div>
        </div>
      </div>

      {/* 선발투수 (경기전) */}
      {status === '예정' && (homeStarterName || awayStarterName) && (
        <div className="px-3 py-2 border-t border-gray-100 flex justify-between text-xs text-gray-600">
          <span>{awayStarterName && `선발: ${awayStarterName}`}</span>
          <span>{homeStarterName && `선발: ${homeStarterName}`}</span>
        </div>
      )}

      {/* 이닝별 점수표 */}
      {status !== '예정' && hasInnings && (
        <div className="border-t border-gray-100 overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="bg-gray-50">
                <th className="text-left px-2 py-1 text-gray-500 font-medium w-12">팀</th>
                {homeTeam.inningScores.map((s) => (
                  <th key={s.inning} className="text-center px-1 py-1 text-gray-500 font-medium w-6">
                    {s.inning}
                  </th>
                ))}
                <th className="text-center px-1 py-1 font-bold text-gray-700 w-6">R</th>
                <th className="text-center px-1 py-1 font-bold text-gray-700 w-6">H</th>
                <th className="text-center px-1 py-1 font-bold text-gray-700 w-6">E</th>
              </tr>
            </thead>
            <tbody>
              {/* 원정팀 (어웨이) */}
              <tr className="border-t border-gray-100">
                <td className="px-2 py-1 text-gray-700 font-medium">{awayTeam.shortName}</td>
                {homeTeam.inningScores.map((s) => (
                  <td key={s.inning} className="text-center px-1 py-1 tabular-nums text-gray-700">
                    {s.awayScore}
                  </td>
                ))}
                <td className="text-center px-1 py-1 font-bold tabular-nums text-gray-900">{awayTeam.score}</td>
                <td className="text-center px-1 py-1 tabular-nums text-gray-700">{awayTeam.teamHits ?? '-'}</td>
                <td className="text-center px-1 py-1 tabular-nums text-gray-700">{awayTeam.teamErrors ?? '-'}</td>
              </tr>
              {/* 홈팀 */}
              <tr className="border-t border-gray-100">
                <td className="px-2 py-1 text-gray-700 font-medium">{homeTeam.shortName}</td>
                {homeTeam.inningScores.map((s) => (
                  <td key={s.inning} className="text-center px-1 py-1 tabular-nums text-gray-700">
                    {s.homeScore}
                  </td>
                ))}
                <td className="text-center px-1 py-1 font-bold tabular-nums text-gray-900">{homeTeam.score}</td>
                <td className="text-center px-1 py-1 tabular-nums text-gray-700">{homeTeam.teamHits ?? '-'}</td>
                <td className="text-center px-1 py-1 tabular-nums text-gray-700">{homeTeam.teamErrors ?? '-'}</td>
              </tr>
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function TeamLogo({ team }: { team: BaseballTeamInfo }) {
  return (
    <div className="w-10 h-10 flex items-center justify-center">
      {team.logo ? (
        <img src={team.logo} alt={team.name} className="w-10 h-10 object-contain" />
      ) : (
        <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center text-xs font-bold text-gray-600">
          {team.shortName.slice(0, 2)}
        </div>
      )}
    </div>
  );
}

export default Scoreboard;
