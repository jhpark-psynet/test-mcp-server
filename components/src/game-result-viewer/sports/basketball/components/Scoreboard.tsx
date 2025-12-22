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
    <div className="w-10 h-10 flex items-center justify-center">
      {team.logo ? (
        <img src={team.logo} alt={team.name} className="w-9 h-9 object-contain" />
      ) : (
        <div className="w-9 h-9 bg-gray-200 rounded-full flex items-center justify-center text-xs font-semibold text-gray-600">
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
    </div>
  );
}

export default Scoreboard;
