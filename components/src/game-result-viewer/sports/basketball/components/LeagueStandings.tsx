import { useState } from 'react';
import type { LeagueStandings as LeagueStandingsType, StandingsTeam, Conference } from '../types';

interface LeagueStandingsProps {
  standings: LeagueStandingsType[];
  homeTeamName?: string;
  awayTeamName?: string;
}

export function LeagueStandings({ standings, homeTeamName, awayTeamName }: LeagueStandingsProps) {
  const hasConferences = standings.length > 1 && standings[0].conference;
  const [activeConference, setActiveConference] = useState<Conference>(
    hasConferences ? (standings[0].conference as Conference) : '동부'
  );

  const currentStandings = hasConferences
    ? standings.find(s => s.conference === activeConference) || standings[0]
    : standings[0];

  return (
    <div className="bg-white border border-gray-200 rounded-lg">
      <div className="px-3 py-2 border-b border-gray-100">
        <h3 className="text-sm font-semibold text-gray-800">리그 순위</h3>
      </div>

      {/* 컨퍼런스 탭 */}
      {hasConferences && (
        <div className="flex mx-2 mt-2 bg-gray-100 rounded-lg p-0.5">
          {standings.map((s) => (
            <button
              key={s.conference}
              onClick={() => setActiveConference(s.conference as Conference)}
              className={`flex-1 py-1.5 text-xs font-semibold rounded-md transition-all ${
                activeConference === s.conference
                  ? 'bg-white text-gray-800 shadow-sm'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              {s.conference}
            </button>
          ))}
        </div>
      )}

      {/* 순위 테이블 */}
      <div className="p-2">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-xs text-gray-600 font-semibold">
              <th className="text-left py-1 w-6">#</th>
              <th className="text-left py-1">팀</th>
              <th className="text-center py-1 w-8">승</th>
              <th className="text-center py-1 w-8">패</th>
              <th className="text-center py-1 w-12">승률</th>
            </tr>
          </thead>
          <tbody>
            {currentStandings.teams.map((team) => (
              <StandingRow
                key={team.rank}
                team={team}
                isHomeTeam={team.shortName === homeTeamName}
                isAwayTeam={team.shortName === awayTeamName}
              />
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function StandingRow({ team, isHomeTeam, isAwayTeam }: { team: StandingsTeam; isHomeTeam: boolean; isAwayTeam: boolean }) {
  const highlight = isHomeTeam || isAwayTeam;
  const teamColor = isHomeTeam ? 'text-purple-700' : isAwayTeam ? 'text-blue-700' : 'text-gray-800';

  return (
    <tr className={`border-t border-gray-100 ${highlight ? 'bg-blue-50' : ''}`}>
      <td className="py-1 text-gray-500 font-medium">{team.rank}</td>
      <td className={`py-1 font-semibold ${teamColor}`}>{team.shortName}</td>
      <td className="text-center py-1 tabular-nums text-gray-700">{team.wins}</td>
      <td className="text-center py-1 tabular-nums text-gray-700">{team.losses}</td>
      <td className="text-center py-1 tabular-nums font-semibold text-gray-800">{team.winRate}</td>
    </tr>
  );
}

export default LeagueStandings;
