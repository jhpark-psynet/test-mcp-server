import { useState } from 'react';
import type { VolleyballTeamInfo, VolleyballPlayerStats as PlayerStatsType } from '../types';

interface PlayerStatsProps {
  homeTeam: VolleyballTeamInfo;
  awayTeam: VolleyballTeamInfo;
}

export function PlayerStats({ homeTeam, awayTeam }: PlayerStatsProps) {
  const [activeTab, setActiveTab] = useState<'home' | 'away'>('home');
  const currentTeam = activeTab === 'home' ? homeTeam : awayTeam;

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
              borderColor: activeTab === 'home' ? homeTeam.primaryColor : 'transparent',
              color: activeTab === 'home' ? homeTeam.primaryColor : '#6b7280'
            }}
          >
            {homeTeam.shortName}
          </button>
          <button
            onClick={() => setActiveTab('away')}
            className="flex-1 px-3 py-2 text-sm font-medium border-b-2 transition-colors duration-150"
            style={{
              borderColor: activeTab === 'away' ? awayTeam.primaryColor : 'transparent',
              color: activeTab === 'away' ? awayTeam.primaryColor : '#6b7280'
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
              <th className="text-xs font-medium text-center px-2 py-1.5 w-10" style={{ color: '#4b5563' }}>SET</th>
              <th className="text-xs font-medium text-center px-2 py-1.5 w-10" style={{ color: '#4b5563' }}>득점</th>
              <th className="text-xs font-medium text-center px-2 py-1.5 w-10" style={{ color: '#4b5563' }}>공격</th>
              <th className="text-xs font-medium text-center px-2 py-1.5 w-10" style={{ color: '#4b5563' }}>블킹</th>
              <th className="text-xs font-medium text-center px-2 py-1.5 w-10" style={{ color: '#4b5563' }}>서브</th>
              <th className="text-xs font-medium text-center px-2 py-1.5 w-10" style={{ color: '#4b5563' }}>디그</th>
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
                      style={{ color: activeTab === 'home' ? homeTeam.primaryColor : awayTeam.primaryColor }}
                    >
                      {player.name}
                    </span>
                    <span className="text-xs" style={{ color: '#6b7280' }}>{player.position}</span>
                  </div>
                </td>
                <td className="text-center text-sm tabular-nums px-2" style={{ color: '#1f2937' }}>{player.sets}</td>
                <td className="text-center text-sm font-medium tabular-nums px-2" style={{ color: '#1f2937' }}>{player.points}</td>
                <td className="text-center text-sm tabular-nums px-2" style={{ color: '#1f2937' }}>{player.kills}</td>
                <td className="text-center text-sm tabular-nums px-2" style={{ color: '#1f2937' }}>{player.blocks}</td>
                <td className="text-center text-sm tabular-nums px-2" style={{ color: '#1f2937' }}>{player.aces}</td>
                <td className="text-center text-sm tabular-nums px-2" style={{ color: '#1f2937' }}>{player.digs}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default PlayerStats;
