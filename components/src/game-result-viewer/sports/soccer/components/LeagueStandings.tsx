import type { LeagueStandings as LeagueStandingsType, SoccerTeamInfo, RecentGameResult } from '../types';

interface LeagueStandingsProps {
  standings: LeagueStandingsType[];
  homeTeam: SoccerTeamInfo;
  awayTeam: SoccerTeamInfo;
}

export function LeagueStandings({ standings, homeTeam, awayTeam }: LeagueStandingsProps) {
  if (!standings || standings.length === 0) return null;

  const currentStandings = standings[0];

  const getResultColor = (result: RecentGameResult) => {
    switch (result) {
      case 'W': return '#2563eb'; // blue-600
      case 'D': return '#6b7280'; // gray-500
      case 'L': return '#dc2626'; // red-600
    }
  };

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
              <th className="text-center py-1.5 w-8">승</th>
              <th className="text-center py-1.5 w-8">무</th>
              <th className="text-center py-1.5 w-8">패</th>
              <th className="text-center py-1.5 w-10">득실</th>
              <th className="text-center py-1.5 w-10">승점</th>
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
                  <td className="text-center py-1.5 tabular-nums" style={{ color: '#1f2937' }}>{team.draws}</td>
                  <td className="text-center py-1.5 tabular-nums" style={{ color: '#1f2937' }}>{team.losses}</td>
                  <td className="text-center py-1.5 tabular-nums" style={{ color: '#1f2937' }}>
                    {team.goalDifference > 0 ? `+${team.goalDifference}` : team.goalDifference}
                  </td>
                  <td className="text-center py-1.5 tabular-nums font-bold" style={{ color: '#1f2937' }}>{team.points}</td>
                  <td className="py-1.5">
                    <div className="flex gap-0.5 justify-end">
                      {team.recentGames.slice(0, 5).map((result, idx) => (
                        <span
                          key={idx}
                          className="w-4 h-4 flex items-center justify-center text-[9px] font-bold rounded text-white"
                          style={{ backgroundColor: getResultColor(result) }}
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
