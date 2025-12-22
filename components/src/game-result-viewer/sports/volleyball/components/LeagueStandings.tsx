import type { LeagueStandings as LeagueStandingsType, VolleyballTeamInfo, RecentGameResult } from '../types';

interface LeagueStandingsProps {
  standings: LeagueStandingsType[];
  homeTeam: VolleyballTeamInfo;
  awayTeam: VolleyballTeamInfo;
}

export function LeagueStandings({ standings, homeTeam, awayTeam }: LeagueStandingsProps) {
  if (!standings || standings.length === 0) return null;

  const currentStandings = standings[0];

  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-sm">
      <div className="px-3 py-2 border-b border-gray-100">
        <h3 className="text-sm font-medium" style={{ color: '#1f2937' }}>리그 순위</h3>
      </div>

      <div className="p-2 overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-xs border-b border-gray-100" style={{ color: '#4b5563' }}>
              <th className="text-left py-1.5 w-8">#</th>
              <th className="text-left py-1.5">팀</th>
              <th className="text-center py-1.5 w-10">승</th>
              <th className="text-center py-1.5 w-10">패</th>
              <th className="text-center py-1.5 w-14">승률</th>
              <th className="text-right py-1.5 w-24">최근 5경기</th>
            </tr>
          </thead>
          <tbody>
            {currentStandings.teams.slice(0, 5).map((team) => {
              const isHomeTeam = team.shortName === homeTeam.shortName;
              const isAwayTeam = team.shortName === awayTeam.shortName;
              const teamColor = isHomeTeam
                ? homeTeam.primaryColor
                : isAwayTeam
                ? awayTeam.primaryColor
                : undefined;

              return (
                <tr
                  key={team.rank}
                  className="border-b border-gray-100"
                  style={{ backgroundColor: isHomeTeam || isAwayTeam ? '#eff6ff' : undefined }}
                >
                  <td className="py-1.5 font-medium" style={{ color: '#4b5563' }}>{team.rank}</td>
                  <td className="py-1.5">
                    <span
                      className="font-medium"
                      style={{ color: teamColor || '#1f2937' }}
                    >
                      {team.shortName}
                    </span>
                  </td>
                  <td className="text-center py-1.5 tabular-nums" style={{ color: '#1f2937' }}>{team.wins}</td>
                  <td className="text-center py-1.5 tabular-nums" style={{ color: '#1f2937' }}>{team.losses}</td>
                  <td className="text-center py-1.5 tabular-nums font-medium" style={{ color: '#1f2937' }}>{team.winRate}</td>
                  <td className="py-1.5">
                    <div className="flex gap-0.5 justify-end">
                      {team.recentGames.slice(0, 5).map((result, idx) => (
                        <span
                          key={idx}
                          className="w-4 h-4 flex items-center justify-center text-[9px] font-bold rounded text-white"
                          style={{ backgroundColor: result === 'W' ? '#2563eb' : '#6b7280' }}
                        >
                          {result}
                        </span>
                      ))}
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default LeagueStandings;
