import { useState } from 'react';
import type { BasketballTeamInfo, BasketballPlayerStats } from '../types';

interface PlayerStatsProps {
  homeTeam: BasketballTeamInfo;
  awayTeam: BasketballTeamInfo;
}

export function PlayerStats({ homeTeam, awayTeam }: PlayerStatsProps) {
  const [activeTab, setActiveTab] = useState<'home' | 'away'>('home');
  const currentTeam = activeTab === 'home' ? homeTeam : awayTeam;

  return (
    <div className="bg-white border border-gray-200 rounded-lg">
      {/* 탭 */}
      <div className="flex border-b border-gray-200">
        <button
          onClick={() => setActiveTab('home')}
          className={`flex-1 px-3 py-2 text-sm font-semibold border-b-2 ${
            activeTab === 'home'
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          {homeTeam.shortName}
        </button>
        <button
          onClick={() => setActiveTab('away')}
          className={`flex-1 px-3 py-2 text-sm font-semibold border-b-2 ${
            activeTab === 'away'
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          {awayTeam.shortName}
        </button>
      </div>

      {/* 선수 스탯 테이블 */}
      <div className="p-2 overflow-x-auto">
        <PlayerStatsTable players={currentTeam.players} />
      </div>
    </div>
  );
}

function PlayerStatsTable({ players }: { players: BasketballPlayerStats[] }) {
  const hasExtendedStats = players.some(p => p.fgm !== undefined || p.steals !== undefined);

  return (
    <table className="w-full text-sm">
      <thead>
        <tr className="border-b border-gray-200">
          <th className="text-xs font-semibold text-gray-600 text-left px-1 py-1">선수</th>
          <th className="text-xs font-semibold text-gray-600 text-center px-1 py-1 w-8">MIN</th>
          <th className="text-xs font-semibold text-gray-600 text-center px-1 py-1 w-8">REB</th>
          <th className="text-xs font-semibold text-gray-600 text-center px-1 py-1 w-8">AST</th>
          <th className="text-xs font-semibold text-gray-600 text-center px-1 py-1 w-8">PTS</th>
          {hasExtendedStats && (
            <>
              <th className="text-xs font-semibold text-gray-600 text-center px-1 py-1 w-10">FG</th>
              <th className="text-xs font-semibold text-gray-600 text-center px-1 py-1 w-10">3P</th>
              <th className="text-xs font-semibold text-gray-600 text-center px-1 py-1 w-8">STL</th>
              <th className="text-xs font-semibold text-gray-600 text-center px-1 py-1 w-8">BLK</th>
            </>
          )}
        </tr>
      </thead>
      <tbody>
        {players.map((player, index) => (
          <tr key={index} className="border-b border-gray-100 hover:bg-gray-50">
            <td className="py-1 px-1">
              <div className="flex items-center gap-1">
                <span className="text-gray-500 text-xs w-4">{player.number}</span>
                <span className="text-sm text-gray-800">{player.name}</span>
                <span className="text-xs text-gray-500">{player.position}</span>
              </div>
            </td>
            <td className="text-center text-sm tabular-nums px-1 text-gray-700">{player.minutes}</td>
            <td className="text-center text-sm tabular-nums px-1 text-gray-700">{player.rebounds}</td>
            <td className="text-center text-sm tabular-nums px-1 text-gray-700">{player.assists}</td>
            <td className="text-center text-sm font-semibold tabular-nums px-1 text-gray-900">{player.points}</td>
            {hasExtendedStats && (
              <>
                <td className="text-center text-xs tabular-nums px-1 text-gray-600">
                  {player.fgm !== undefined ? `${player.fgm}/${player.fga}` : '-'}
                </td>
                <td className="text-center text-xs tabular-nums px-1 text-gray-600">
                  {player.tpm !== undefined ? `${player.tpm}/${player.tpa}` : '-'}
                </td>
                <td className="text-center text-sm tabular-nums px-1 text-gray-700">{player.steals ?? '-'}</td>
                <td className="text-center text-sm tabular-nums px-1 text-gray-700">{player.blocks ?? '-'}</td>
              </>
            )}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default PlayerStats;
