import type { SoccerTeamInfo, GameStatus, SoccerLeague, SoccerPeriod, HalfScores } from '../types';

interface ScoreboardProps {
  league: SoccerLeague;
  date: string;
  time?: string;
  status: GameStatus;
  currentPeriod?: SoccerPeriod;
  currentMinute?: number;
  addedTime?: number;
  homeTeam: SoccerTeamInfo;
  awayTeam: SoccerTeamInfo;
}

export function Scoreboard({
  league,
  date,
  time,
  status,
  currentPeriod,
  currentMinute,
  addedTime,
  homeTeam,
  awayTeam,
}: ScoreboardProps) {
  const homeColor = homeTeam.primaryColor || '#3b82f6';
  const awayColor = awayTeam.primaryColor || '#ef4444';
  const homeLeads = homeTeam.score > awayTeam.score;
  const awayLeads = awayTeam.score > homeTeam.score;
  const isLive = status === '진행중';
  const isFinished = status === '종료';
  const isScheduled = status === '예정';

  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-sm">
      {/* 헤더 */}
      <div className="flex justify-between items-center px-3 py-2 border-b border-gray-100">
        <div className="flex items-center gap-2">
          <span
            className="font-medium text-sm px-2 py-0.5 rounded text-white"
            style={{ background: `linear-gradient(135deg, ${homeColor}, ${awayColor})` }}
          >
            {league}
          </span>
          <span style={{ color: '#6b7280' }} className="text-sm">{date}</span>
          {time && isScheduled && (
            <span style={{ color: '#4b5563' }} className="text-sm">{time}</span>
          )}
          {currentMinute && isLive && (
            <span style={{ color: '#4b5563' }} className="text-sm">
              {currentMinute}{addedTime ? `+${addedTime}` : ''}'
            </span>
          )}
        </div>
        <StatusBadge status={status} />
      </div>

      {/* 스코어보드 */}
      <div className="flex items-center justify-center py-4 px-3">
        {/* 홈팀 */}
        <div className="flex flex-col items-center gap-1 flex-1">
          <TeamLogo team={homeTeam} />
          <div className="text-center">
            <div className="font-medium text-sm" style={{ color: '#1f2937' }}>{homeTeam.shortName}</div>
            <div className="text-xs" style={{ color: '#6b7280' }}>{homeTeam.record}</div>
          </div>
        </div>

        {/* 점수 */}
        <div className="flex flex-col items-center gap-1 px-4">
          <div className="flex items-center gap-3">
            <span
              className="text-3xl font-bold tabular-nums"
              style={{ color: homeLeads ? homeColor : '#9ca3af' }}
            >
              {isScheduled ? '-' : homeTeam.score}
            </span>
            <span className="text-xl" style={{ color: '#6b7280' }}>-</span>
            <span
              className="text-3xl font-bold tabular-nums"
              style={{ color: awayLeads ? awayColor : '#9ca3af' }}
            >
              {isScheduled ? '-' : awayTeam.score}
            </span>
          </div>
          {isLive && currentMinute && (
            <span className="text-xs font-medium" style={{ color: '#dc2626' }}>
              {currentMinute}{addedTime ? `+${addedTime}` : ''}'
            </span>
          )}
        </div>

        {/* 원정팀 */}
        <div className="flex flex-col items-center gap-1 flex-1">
          <TeamLogo team={awayTeam} />
          <div className="text-center">
            <div className="font-medium text-sm" style={{ color: '#1f2937' }}>{awayTeam.shortName}</div>
            <div className="text-xs" style={{ color: '#6b7280' }}>{awayTeam.record}</div>
          </div>
        </div>
      </div>

      {/* 전/후반 점수 */}
      {!isScheduled && homeTeam.halfScores && awayTeam.halfScores && (
        <HalfScoresTable
          homeTeam={homeTeam}
          awayTeam={awayTeam}
          currentPeriod={currentPeriod}
          isLive={isLive}
        />
      )}
    </div>
  );
}

function StatusBadge({ status }: { status: GameStatus }) {
  switch (status) {
    case '진행중':
      return (
        <span className="text-sm font-medium flex items-center gap-1" style={{ color: '#dc2626' }}>
          <span className="w-2 h-2 rounded-full animate-pulse" style={{ backgroundColor: '#dc2626' }} />
          LIVE
        </span>
      );
    case '종료':
      return <span className="text-sm font-medium" style={{ color: '#4b5563' }}>종료</span>;
    case '예정':
      return <span className="text-sm font-medium" style={{ color: '#2563eb' }}>예정</span>;
    default:
      return null;
  }
}

function TeamLogo({ team }: { team: SoccerTeamInfo }) {
  const initials = team.shortName.slice(0, 2);
  const primaryColor = team.primaryColor || '#3b82f6';
  const secondaryColor = team.secondaryColor || '#1d4ed8';

  return (
    <div className="w-10 h-10 flex items-center justify-center">
      {team.logo ? (
        <img src={team.logo} alt={team.name} className="w-9 h-9 object-contain" />
      ) : (
        <div
          className="w-9 h-9 rounded-full flex items-center justify-center text-xs font-semibold text-white"
          style={{ background: `linear-gradient(135deg, ${primaryColor}, ${secondaryColor})` }}
        >
          {initials}
        </div>
      )}
    </div>
  );
}

function HalfScoresTable({
  homeTeam,
  awayTeam,
  currentPeriod,
  isLive,
}: {
  homeTeam: SoccerTeamInfo;
  awayTeam: SoccerTeamInfo;
  currentPeriod?: SoccerPeriod;
  isLive: boolean;
}) {
  const homeS = homeTeam.halfScores!;
  const awayS = awayTeam.halfScores!;
  const homeColor = homeTeam.primaryColor || '#3b82f6';
  const awayColor = awayTeam.primaryColor || '#ef4444';

  const periods: { label: string; home: number; away: number }[] = [
    { label: '전반', home: homeS.firstHalf, away: awayS.firstHalf },
    { label: '후반', home: homeS.secondHalf, away: awayS.secondHalf },
  ];

  if (homeS.extraFirstHalf !== undefined) {
    periods.push({ label: '연장전반', home: homeS.extraFirstHalf, away: awayS.extraFirstHalf ?? 0 });
  }
  if (homeS.extraSecondHalf !== undefined) {
    periods.push({ label: '연장후반', home: homeS.extraSecondHalf, away: awayS.extraSecondHalf ?? 0 });
  }
  if (homeS.penalties !== undefined) {
    periods.push({ label: 'PK', home: homeS.penalties, away: awayS.penalties ?? 0 });
  }

  return (
    <div className="border-t border-gray-100 px-3 py-2">
      <table className="w-full text-sm">
        <thead>
          <tr style={{ color: '#4b5563' }}>
            <th className="text-left font-medium py-1 w-16">팀</th>
            {periods.map((p) => (
              <th
                key={p.label}
                className="text-center font-medium py-1 w-12"
                style={{ color: isLive && currentPeriod === p.label ? '#dc2626' : '#4b5563' }}
              >
                {p.label}
              </th>
            ))}
            <th className="text-center font-medium py-1 w-14">TOTAL</th>
          </tr>
        </thead>
        <tbody style={{ color: '#1f2937' }}>
          <tr>
            <td className="text-left py-1 font-medium" style={{ color: homeColor }}>
              {homeTeam.shortName}
            </td>
            {periods.map((p) => {
              const isCurrent = isLive && currentPeriod === p.label;
              const homeWon = !isCurrent && p.home > p.away;

              return (
                <td
                  key={`home-${p.label}`}
                  className="text-center py-1 tabular-nums"
                  style={{
                    color: isCurrent ? '#dc2626' : homeWon ? '#2563eb' : '#1f2937',
                    fontWeight: isCurrent || homeWon ? 700 : 400
                  }}
                >
                  {p.home}
                </td>
              );
            })}
            <td className="text-center py-1 tabular-nums font-bold" style={{ color: homeColor }}>
              {homeTeam.score}
            </td>
          </tr>
          <tr>
            <td className="text-left py-1 font-medium" style={{ color: awayColor }}>
              {awayTeam.shortName}
            </td>
            {periods.map((p) => {
              const isCurrent = isLive && currentPeriod === p.label;
              const awayWon = !isCurrent && p.away > p.home;

              return (
                <td
                  key={`away-${p.label}`}
                  className="text-center py-1 tabular-nums"
                  style={{
                    color: isCurrent ? '#dc2626' : awayWon ? '#2563eb' : '#1f2937',
                    fontWeight: isCurrent || awayWon ? 700 : 400
                  }}
                >
                  {p.away}
                </td>
              );
            })}
            <td className="text-center py-1 tabular-nums font-bold" style={{ color: awayColor }}>
              {awayTeam.score}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  );
}

export default Scoreboard;
