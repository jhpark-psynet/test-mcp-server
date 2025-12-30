import type { SoccerTeamInfo, HeadToHeadRecord, RecentGameResult, GameStatus, SoccerLeague } from '../types';

interface TeamComparisonProps {
  league: SoccerLeague;
  date: string;
  time?: string;
  status: GameStatus;
  homeTeam: SoccerTeamInfo;
  awayTeam: SoccerTeamInfo;
  headToHead?: HeadToHeadRecord;
}

export function TeamComparison({
  league,
  date,
  time,
  status,
  homeTeam,
  awayTeam,
  headToHead,
}: TeamComparisonProps) {
  const showHeader = status !== '예정';
  const homeColor = homeTeam.primaryColor || '#3b82f6';
  const awayColor = awayTeam.primaryColor || '#ef4444';

  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-sm">
      {showHeader && (
        <div className="px-3 py-2 border-b border-gray-100">
          <h3 className="text-sm font-medium" style={{ color: '#1f2937' }}>양팀 비교</h3>
        </div>
      )}

      {/* 팀 헤더 */}
      <div className="px-3 py-2 border-b border-gray-100">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <TeamLogo team={homeTeam} size="sm" />
            <span className="font-medium" style={{ color: '#1f2937' }}>{homeTeam.shortName}</span>
          </div>

          <div className="text-center">
            {status === '예정' ? (
              <div>
                <div className="text-xs" style={{ color: '#6b7280' }}>{league}</div>
                <div className="text-sm font-medium" style={{ color: '#4b5563' }}>{date}</div>
                {time && <div className="text-xs" style={{ color: '#6b7280' }}>{time}</div>}
              </div>
            ) : (
              <span style={{ color: '#6b7280' }}>vs</span>
            )}
          </div>

          <div className="flex items-center gap-2">
            <span className="font-medium" style={{ color: '#1f2937' }}>{awayTeam.shortName}</span>
            <TeamLogo team={awayTeam} size="sm" />
          </div>
        </div>
      </div>

      {/* 최근 5경기 */}
      {(homeTeam.recentGames || awayTeam.recentGames) && (
        <div className="px-3 py-2 border-b border-gray-100">
          <div className="text-xs mb-2 text-center" style={{ color: '#6b7280' }}>최근 5경기</div>
          <div className="flex items-center justify-between">
            <RecentGamesDisplay games={homeTeam.recentGames} align="left" />
            <RecentGamesDisplay games={awayTeam.recentGames} align="right" />
          </div>
        </div>
      )}

      {/* 맞대결 기록 */}
      {headToHead && (
        <div className="px-3 py-2">
          <div className="text-xs mb-2 text-center" style={{ color: '#6b7280' }}>
            상대 전적 (최근 {headToHead.totalGames}경기)
          </div>
          <div className="flex items-center justify-center gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold" style={{ color: homeColor }}>
                {headToHead.homeWins}
              </div>
              <div className="text-xs" style={{ color: '#6b7280' }}>승</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold" style={{ color: '#4b5563' }}>{headToHead.draws}</div>
              <div className="text-xs" style={{ color: '#6b7280' }}>무</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold" style={{ color: awayColor }}>
                {headToHead.awayWins}
              </div>
              <div className="text-xs" style={{ color: '#6b7280' }}>승</div>
            </div>
          </div>

          {headToHead.recentMatches && headToHead.recentMatches.length > 0 && (
            <div className="mt-3 space-y-1">
              {headToHead.recentMatches.slice(0, 5).map((match, idx) => (
                <div key={idx} className="flex items-center justify-between text-xs">
                  <span style={{ color: '#6b7280' }}>{match.date}</span>
                  <div className="flex items-center gap-2">
                    <span
                      style={{
                        color: match.winner === 'home' ? homeColor : '#6b7280',
                        fontWeight: match.winner === 'home' ? 700 : 400
                      }}
                    >
                      {match.homeScore}
                    </span>
                    <span style={{ color: '#6b7280' }}>-</span>
                    <span
                      style={{
                        color: match.winner === 'away' ? awayColor : '#6b7280',
                        fontWeight: match.winner === 'away' ? 700 : 400
                      }}
                    >
                      {match.awayScore}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function TeamLogo({ team, size = 'md' }: { team: SoccerTeamInfo; size?: 'sm' | 'md' }) {
  const sizeClass = size === 'sm' ? 'w-8 h-8' : 'w-10 h-10';
  const textSize = size === 'sm' ? 'text-[10px]' : 'text-xs';
  const primaryColor = team.primaryColor || '#3b82f6';
  const secondaryColor = team.secondaryColor || '#1d4ed8';

  return (
    <div className={`${sizeClass} flex items-center justify-center`}>
      {team.logo ? (
        <img src={team.logo} alt={team.name} className={`${sizeClass} object-contain`} />
      ) : (
        <div
          className={`${sizeClass} rounded-full flex items-center justify-center ${textSize} font-semibold text-white`}
          style={{ background: `linear-gradient(135deg, ${primaryColor}, ${secondaryColor})` }}
        >
          {team.shortName.slice(0, 2)}
        </div>
      )}
    </div>
  );
}

function RecentGamesDisplay({ games, align }: { games?: RecentGameResult[]; align: 'left' | 'right' }) {
  if (!games || games.length === 0) return null;

  const getResultColor = (result: RecentGameResult) => {
    switch (result) {
      case 'W': return '#2563eb'; // blue-600
      case 'D': return '#6b7280'; // gray-500
      case 'L': return '#dc2626'; // red-600
    }
  };

  return (
    <div className={`flex gap-1 ${align === 'right' ? 'flex-row-reverse' : ''}`}>
      {games.slice(0, 5).map((result, idx) => (
        <div
          key={idx}
          className="w-5 h-5 flex items-center justify-center text-[10px] font-bold rounded-sm text-white"
          style={{ backgroundColor: getResultColor(result) }}
        >
          {result}
        </div>
      ))}
    </div>
  );
}

export default TeamComparison;
