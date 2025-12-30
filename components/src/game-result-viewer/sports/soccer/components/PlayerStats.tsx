import { useState } from 'react';
import type { SoccerTeamInfo, SoccerPlayerStats as PlayerStatsType } from '../types';

interface PlayerStatsProps {
  homeTeam: SoccerTeamInfo;
  awayTeam: SoccerTeamInfo;
}

export function PlayerStats({ homeTeam, awayTeam }: PlayerStatsProps) {
  const [activeTab, setActiveTab] = useState<'home' | 'away'>('home');
  const currentTeam = activeTab === 'home' ? homeTeam : awayTeam;

  const homeColor = homeTeam.primaryColor || '#3b82f6';
  const awayColor = awayTeam.primaryColor || '#ef4444';

  if (currentTeam.players.length === 0) return null;

  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-sm">
      {/* 탭 */}
      <div className="border-b border-gray-200">
        <div className="flex">
          <button
            onClick={() => setActiveTab('home')}
            className="flex-1 px-3 py-2 text-sm font-medium border-b-2 transition-colors duration-150"
            style={{
              borderColor: activeTab === 'home' ? homeColor : 'transparent',
              color: activeTab === 'home' ? homeColor : '#6b7280'
            }}
          >
            {homeTeam.shortName}
          </button>
          <button
            onClick={() => setActiveTab('away')}
            className="flex-1 px-3 py-2 text-sm font-medium border-b-2 transition-colors duration-150"
            style={{
              borderColor: activeTab === 'away' ? awayColor : 'transparent',
              color: activeTab === 'away' ? awayColor : '#6b7280'
            }}
          >
            {awayTeam.shortName}
          </button>
        </div>
      </div>

      {/* 선수 스탯 테이블 */}
      <div className="p-2 overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-200" style={{ backgroundColor: '#f9fafb' }}>
              <th className="text-xs font-medium text-left px-2 py-1.5" style={{ color: '#4b5563' }}>선수</th>
              <th className="text-xs font-medium text-center px-2 py-1.5 w-10" style={{ color: '#4b5563' }}>MIN</th>
              <th className="text-xs font-medium text-center px-2 py-1.5 w-10" style={{ color: '#4b5563' }}>골</th>
              <th className="text-xs font-medium text-center px-2 py-1.5 w-10" style={{ color: '#4b5563' }}>AS</th>
              <th className="text-xs font-medium text-center px-2 py-1.5 w-10" style={{ color: '#4b5563' }}>슈팅</th>
              <th className="text-xs font-medium text-center px-2 py-1.5 w-10" style={{ color: '#4b5563' }}>패스</th>
              <th className="text-xs font-medium text-center px-2 py-1.5 w-10" style={{ color: '#4b5563' }}>태클</th>
            </tr>
          </thead>
          <tbody>
            {currentTeam.players.map((player, index) => (
              <tr key={index} className="border-b border-gray-100 hover:bg-gray-50 transition-colors duration-150">
                <td className="py-1.5 px-2">
                  <div className="flex items-center gap-1">
                    <span className="text-xs w-5" style={{ color: '#6b7280' }}>{player.number}</span>
                    <span
                      className="text-sm"
                      style={{ color: activeTab === 'home' ? homeColor : awayColor }}
                    >
                      {player.name}
                    </span>
                    <span className="text-xs" style={{ color: '#6b7280' }}>{player.position}</span>
                    {player.yellowCards > 0 && (
                      <span className="w-2.5 h-3 rounded-sm" style={{ backgroundColor: '#f59e0b' }} title="옐로카드" />
                    )}
                    {player.redCards > 0 && (
                      <span className="w-2.5 h-3 rounded-sm" style={{ backgroundColor: '#dc2626' }} title="레드카드" />
                    )}
                  </div>
                </td>
                <td className="text-center text-sm tabular-nums px-2" style={{ color: '#1f2937' }}>{player.minutes}</td>
                <td className="text-center text-sm font-medium tabular-nums px-2" style={{ color: '#1f2937' }}>{player.goals}</td>
                <td className="text-center text-sm tabular-nums px-2" style={{ color: '#1f2937' }}>{player.assists}</td>
                <td className="text-center text-sm tabular-nums px-2" style={{ color: '#1f2937' }}>{player.shots}</td>
                <td className="text-center text-sm tabular-nums px-2" style={{ color: '#1f2937' }}>{player.passes}</td>
                <td className="text-center text-sm tabular-nums px-2" style={{ color: '#1f2937' }}>{player.tackles}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default PlayerStats;
