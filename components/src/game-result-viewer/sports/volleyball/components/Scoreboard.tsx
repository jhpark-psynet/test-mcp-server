import type { VolleyballTeamInfo, GameStatus, VolleyballLeague, SetScores } from '../types';

interface ScoreboardProps {
  league: VolleyballLeague;
  date: string;
  time?: string;
  status: GameStatus;
  currentSet?: number;
  homeTeam: VolleyballTeamInfo;
  awayTeam: VolleyballTeamInfo;
}

export function Scoreboard({
  league,
  date,
  time,
  status,
  currentSet,
  homeTeam,
  awayTeam,
}: ScoreboardProps) {
  const homeColor = homeTeam.primaryColor;
  const awayColor = awayTeam.primaryColor;
  const homeLeads = homeTeam.setsWon > awayTeam.setsWon;
  const awayLeads = awayTeam.setsWon > homeTeam.setsWon;
  const isLive = status === '경기중';
  const isFinished = status === '경기종료';

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
          {time && status === '경기전' && (
            <span style={{ color: '#4b5563' }} className="text-sm">{time}</span>
          )}
          {currentSet && isLive && (
            <span style={{ color: '#4b5563' }} className="text-sm">{currentSet}세트</span>
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

        {/* 세트 점수 */}
        <div className="flex items-center gap-3 px-4">
          <span
            className="text-3xl font-bold tabular-nums"
            style={{ color: homeLeads ? homeColor : '#9ca3af' }}
          >
            {status === '경기전' ? '-' : homeTeam.setsWon}
          </span>
          <span className="text-xl" style={{ color: '#6b7280' }}>vs</span>
          <span
            className="text-3xl font-bold tabular-nums"
            style={{ color: awayLeads ? awayColor : '#9ca3af' }}
          >
            {status === '경기전' ? '-' : awayTeam.setsWon}
          </span>
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

      {/* 세트별 점수 */}
      {status !== '경기전' && homeTeam.setScores && awayTeam.setScores && (
        <SetScoresTable
          homeTeam={homeTeam}
          awayTeam={awayTeam}
          currentSet={currentSet}
          isLive={isLive}
        />
      )}
    </div>
  );
}

function StatusBadge({ status }: { status: GameStatus }) {
  switch (status) {
    case '경기중':
      return (
        <span className="text-sm font-medium flex items-center gap-1" style={{ color: '#dc2626' }}>
          <span className="w-2 h-2 rounded-full animate-pulse" style={{ backgroundColor: '#dc2626' }} />
          LIVE
        </span>
      );
    case '경기종료':
      return <span className="text-sm font-medium" style={{ color: '#4b5563' }}>종료</span>;
    case '경기전':
      return <span className="text-sm font-medium" style={{ color: '#2563eb' }}>예정</span>;
    default:
      return null;
  }
}

function TeamLogo({ team }: { team: VolleyballTeamInfo }) {
  const initials = team.shortName.slice(0, 2);

  return (
    <div className="w-10 h-10 flex items-center justify-center">
      {team.logo ? (
        <img src={team.logo} alt={team.name} className="w-9 h-9 object-contain" />
      ) : (
        <div
          className="w-9 h-9 rounded-full flex items-center justify-center text-xs font-semibold text-white"
          style={{ background: `linear-gradient(135deg, ${team.primaryColor}, ${team.secondaryColor})` }}
        >
          {initials}
        </div>
      )}
    </div>
  );
}

function SetScoresTable({
  homeTeam,
  awayTeam,
  currentSet,
  isLive,
}: {
  homeTeam: VolleyballTeamInfo;
  awayTeam: VolleyballTeamInfo;
  currentSet?: number;
  isLive: boolean;
}) {
  const homeS = homeTeam.setScores!;
  const awayS = awayTeam.setScores!;

  const sets: { label: string; home: number; away: number }[] = [
    { label: 'SET1', home: homeS.set1, away: awayS.set1 },
    { label: 'SET2', home: homeS.set2, away: awayS.set2 },
    { label: 'SET3', home: homeS.set3, away: awayS.set3 },
  ];

  if (homeS.set4 !== undefined) {
    sets.push({ label: 'SET4', home: homeS.set4, away: awayS.set4 ?? 0 });
  }
  if (homeS.set5 !== undefined) {
    sets.push({ label: 'SET5', home: homeS.set5, away: awayS.set5 ?? 0 });
  }

  return (
    <div className="border-t border-gray-100 px-3 py-2">
      <table className="w-full text-sm">
        <thead>
          <tr style={{ color: '#4b5563' }}>
            <th className="text-left font-medium py-1 w-16">팀</th>
            {sets.map((s, idx) => (
              <th
                key={s.label}
                className="text-center font-medium py-1 w-12"
                style={{ color: isLive && currentSet === idx + 1 ? '#dc2626' : '#4b5563' }}
              >
                {s.label}
              </th>
            ))}
            <th className="text-center font-medium py-1 w-14">SETS</th>
          </tr>
        </thead>
        <tbody style={{ color: '#1f2937' }}>
          <tr>
            <td className="text-left py-1 font-medium" style={{ color: homeTeam.primaryColor }}>
              {homeTeam.shortName}
            </td>
            {sets.map((s, idx) => {
              const isCurrent = isLive && currentSet === idx + 1;
              const homeWon = !isCurrent && s.home > s.away;

              return (
                <td
                  key={`home-${s.label}`}
                  className="text-center py-1 tabular-nums"
                  style={{
                    color: isCurrent ? '#dc2626' : homeWon ? '#2563eb' : '#1f2937',
                    fontWeight: isCurrent || homeWon ? 700 : 400
                  }}
                >
                  {s.home}
                </td>
              );
            })}
            <td className="text-center py-1 tabular-nums font-bold" style={{ color: homeTeam.primaryColor }}>
              {homeTeam.setsWon}
            </td>
          </tr>
          <tr>
            <td className="text-left py-1 font-medium" style={{ color: awayTeam.primaryColor }}>
              {awayTeam.shortName}
            </td>
            {sets.map((s, idx) => {
              const isCurrent = isLive && currentSet === idx + 1;
              const awayWon = !isCurrent && s.away > s.home;

              return (
                <td
                  key={`away-${s.label}`}
                  className="text-center py-1 tabular-nums"
                  style={{
                    color: isCurrent ? '#dc2626' : awayWon ? '#2563eb' : '#1f2937',
                    fontWeight: isCurrent || awayWon ? 700 : 400
                  }}
                >
                  {s.away}
                </td>
              );
            })}
            <td className="text-center py-1 tabular-nums font-bold" style={{ color: awayTeam.primaryColor }}>
              {awayTeam.setsWon}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  );
}

export default Scoreboard;
