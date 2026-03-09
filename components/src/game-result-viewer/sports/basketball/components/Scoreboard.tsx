import type { BasketballTeamInfo, GameStatus, BasketballLeague } from '../types';

interface ScoreboardProps {
  league: BasketballLeague;
  date: string;
  time?: string;
  status: GameStatus;
  venue?: string;
  homeTeam: BasketballTeamInfo;
  awayTeam: BasketballTeamInfo;
}

export function Scoreboard({ league, date, time, status, venue, homeTeam, awayTeam }: ScoreboardProps) {
  const getLeagueColor = (league: string) => {
    switch (league) {
      case 'NBA': return 'text-blue-600';
      case 'KBL': return 'text-orange-600';
      case 'WKBL': return 'text-purple-600';
      default: return 'text-gray-700';
    }
  };

  const getStatusColor = (status: GameStatus) => {
    switch (status) {
      case '종료': return 'text-gray-600';
      case '진행중': return 'text-red-600';
      case '예정': return 'text-blue-600';
      default: return 'text-gray-600';
    }
  };

  const TeamLogo = ({ team }: { team: BasketballTeamInfo }) => (
    <div className="w-12 h-12 flex items-center justify-center">
      {team.logo ? (
        <img src={team.logo} alt={team.name} className="w-11 h-11 object-contain" />
      ) : (
        <div className="w-11 h-11 bg-gray-200 rounded-full flex items-center justify-center text-sm font-semibold text-gray-600">
          {team.shortName.slice(0, 2)}
        </div>
      )}
    </div>
  );

  return (
    <div className="bg-white rounded-lg border border-gray-200">
      {/* 헤더 */}
      <div className="flex justify-between items-center px-3 py-1.5 border-b border-gray-100">
        <div className="flex flex-col">
          <div className="flex items-center gap-2">
            <span className={`font-semibold text-sm ${getLeagueColor(league)}`}>{league}</span>
            <span className="text-gray-600 text-sm">{date}</span>
            {time && status === '예정' && (
              <span className="text-gray-700 text-sm">{time}</span>
            )}
          </div>
          {venue && (
            <span className="text-gray-500 text-xs">{venue}</span>
          )}
        </div>
        <span className={`text-sm font-semibold ${getStatusColor(status)}`}>
          {status}
        </span>
      </div>

      {/* 스코어보드 */}
      <div className="flex items-center justify-center py-3 px-2">
        {/* 홈팀 */}
        <div className="flex flex-col items-center gap-1 flex-1">
          <TeamLogo team={homeTeam} />
          <div className="text-center">
            <div className="font-semibold text-sm text-gray-800">{homeTeam.shortName}</div>
            {homeTeam.record && <div className="text-xs text-gray-500">{homeTeam.record}</div>}
          </div>
        </div>

        {/* 점수 */}
        <div className="flex items-center gap-3 px-4">
          <span className="text-3xl font-bold text-gray-900 tabular-nums">
            {status === '예정' ? '-' : homeTeam.score}
          </span>
          <span className="text-xl text-gray-400">vs</span>
          <span className="text-3xl font-bold text-gray-900 tabular-nums">
            {status === '예정' ? '-' : awayTeam.score}
          </span>
        </div>

        {/* 원정팀 */}
        <div className="flex flex-col items-center gap-1 flex-1">
          <TeamLogo team={awayTeam} />
          <div className="text-center">
            <div className="font-semibold text-sm text-gray-800">{awayTeam.shortName}</div>
            {awayTeam.record && <div className="text-xs text-gray-500">{awayTeam.record}</div>}
          </div>
        </div>
      </div>

      {/* 쿼터별 점수 */}
      {status !== '예정' && (homeTeam.quarterScores || awayTeam.quarterScores) && (() => {
        const hq = homeTeam.quarterScores;
        const aq = awayTeam.quarterScores;
        const otCount = Math.max(hq?.ot?.length ?? 0, aq?.ot?.length ?? 0);
        const hTotal = homeTeam.score;
        const aTotal = awayTeam.score;
        return (
          <div className="border-t border-gray-100 px-3 pb-2 overflow-x-auto">
            <table className="w-full text-xs text-center">
              <thead>
                <tr className="text-gray-400">
                  <th className="py-1 text-left font-medium w-16">팀</th>
                  <th className="py-1 font-medium">Q1</th>
                  <th className="py-1 font-medium">Q2</th>
                  <th className="py-1 font-medium">Q3</th>
                  <th className="py-1 font-medium">Q4</th>
                  {Array.from({ length: otCount }, (_, i) => (
                    <th key={i} className="py-1 font-medium">OT{otCount > 1 ? i + 1 : ''}</th>
                  ))}
                  <th className="py-1 font-semibold text-gray-600">합계</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-t border-gray-100">
                  <td className="py-1 text-left text-gray-600 font-medium truncate">{homeTeam.shortName}</td>
                  <td className="py-1 text-gray-700">{hq?.q1 ?? '-'}</td>
                  <td className="py-1 text-gray-700">{hq?.q2 ?? '-'}</td>
                  <td className="py-1 text-gray-700">{hq?.q3 ?? '-'}</td>
                  <td className="py-1 text-gray-700">{hq?.q4 ?? '-'}</td>
                  {Array.from({ length: otCount }, (_, i) => (
                    <td key={i} className="py-1 text-gray-700">{hq?.ot?.[i] ?? '-'}</td>
                  ))}
                  <td className="py-1 font-bold text-gray-900">{hTotal}</td>
                </tr>
                <tr className="border-t border-gray-100">
                  <td className="py-1 text-left text-gray-600 font-medium truncate">{awayTeam.shortName}</td>
                  <td className="py-1 text-gray-700">{aq?.q1 ?? '-'}</td>
                  <td className="py-1 text-gray-700">{aq?.q2 ?? '-'}</td>
                  <td className="py-1 text-gray-700">{aq?.q3 ?? '-'}</td>
                  <td className="py-1 text-gray-700">{aq?.q4 ?? '-'}</td>
                  {Array.from({ length: otCount }, (_, i) => (
                    <td key={i} className="py-1 text-gray-700">{aq?.ot?.[i] ?? '-'}</td>
                  ))}
                  <td className="py-1 font-bold text-gray-900">{aTotal}</td>
                </tr>
              </tbody>
            </table>
          </div>
        );
      })()}
    </div>
  );
}

export default Scoreboard;
