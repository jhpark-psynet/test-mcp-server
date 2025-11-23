import { useState } from 'react';
import type { GameData } from './types';

interface GameResultViewerProps {
  data: GameData;
}

export function GameResultViewer({ data }: GameResultViewerProps) {
  const [activeTab, setActiveTab] = useState<'home' | 'away' | 'records'>('home');

  // Game status color
  const getStatusColor = (status: string) => {
    switch (status) {
      case '종료': return 'text-gray-600';
      case '진행중': return 'text-red-500';
      default: return 'text-blue-500';
    }
  };

  // League color
  const getLeagueColor = (league: string) => {
    switch (league) {
      case 'NBA': return 'text-blue-600';
      case 'KBL': return 'text-orange-600';
      case 'WKBL': return 'text-pink-600';
      default: return 'text-gray-600';
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto bg-white border border-gray-200 rounded-sm shadow-sm">
      {/* Header: League, Date, Status */}
      <div className="flex justify-between items-center px-4 py-2 border-b border-gray-100">
        <div className="flex items-center gap-2">
          <span className={`font-medium ${getLeagueColor(data.league)}`}>
            {data.league}
          </span>
          <span className="text-gray-400 text-sm">{data.date}</span>
        </div>
        <span className={`text-sm font-medium ${getStatusColor(data.status)}`}>
          {data.status}
        </span>
      </div>

      {/* Scoreboard */}
      <div className="flex items-center justify-center py-6 px-4">
        {/* Home Team */}
        <div className="flex flex-col items-center gap-2 flex-1">
          <div className="w-12 h-12 flex items-center justify-center">
            {data.homeTeam.logo ? (
              <img
                src={data.homeTeam.logo}
                alt={data.homeTeam.name}
                className="w-10 h-10 object-contain"
              />
            ) : (
              <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center text-xs font-bold text-gray-600">
                {data.homeTeam.shortName.slice(0, 2)}
              </div>
            )}
          </div>
          <div className="text-center">
            <div className="font-medium text-gray-900">{data.homeTeam.name}</div>
            <div className="text-xs text-gray-500">{data.homeTeam.record}</div>
          </div>
        </div>

        {/* Score */}
        <div className="flex items-center gap-4 px-6">
          <span className="text-4xl font-bold text-gray-900 tabular-nums">
            {data.homeTeam.score}
          </span>
          <span className="text-2xl text-gray-400">-</span>
          <span className="text-4xl font-bold text-gray-900 tabular-nums">
            {data.awayTeam.score}
          </span>
        </div>

        {/* Away Team */}
        <div className="flex flex-col items-center gap-2 flex-1">
          <div className="w-12 h-12 flex items-center justify-center">
            {data.awayTeam.logo ? (
              <img
                src={data.awayTeam.logo}
                alt={data.awayTeam.name}
                className="w-10 h-10 object-contain"
              />
            ) : (
              <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center text-xs font-bold text-gray-600">
                {data.awayTeam.shortName.slice(0, 2)}
              </div>
            )}
          </div>
          <div className="text-center">
            <div className="font-medium text-gray-900">{data.awayTeam.name}</div>
            <div className="text-xs text-gray-500">{data.awayTeam.record}</div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <div className="flex justify-around">
          <button
            onClick={() => setActiveTab('home')}
            className={`px-4 py-2 text-sm border-b-2 transition-colors ${
              activeTab === 'home'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            {data.homeTeam.shortName}
          </button>
          <button
            onClick={() => setActiveTab('away')}
            className={`px-4 py-2 text-sm border-b-2 transition-colors ${
              activeTab === 'away'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            {data.awayTeam.shortName}
          </button>
          {data.gameRecords && data.gameRecords.length > 0 && (
            <button
              onClick={() => setActiveTab('records')}
              className={`px-4 py-2 text-sm border-b-2 transition-colors ${
                activeTab === 'records'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              경기 기록
            </button>
          )}
        </div>
      </div>

      {/* Tab Content */}
      <div className="p-4">
        {activeTab === 'home' && <PlayerStatsTable players={data.homeTeam.players} />}
        {activeTab === 'away' && <PlayerStatsTable players={data.awayTeam.players} />}
        {activeTab === 'records' && data.gameRecords && (
          <GameRecordsTable
            records={data.gameRecords}
            homeTeam={data.homeTeam.shortName}
            awayTeam={data.awayTeam.shortName}
          />
        )}
      </div>
    </div>
  );
}

// Player stats table
function PlayerStatsTable({ players }: { players: GameData['homeTeam']['players'] }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="bg-gray-50 border-b border-gray-200">
            <th className="text-xs font-medium text-gray-600 text-left px-3 py-2 w-[200px]">선수</th>
            <th className="text-xs font-medium text-gray-600 text-right px-3 py-2 w-[60px]">MIN</th>
            <th className="text-xs font-medium text-gray-600 text-right px-3 py-2 w-[60px]">REB</th>
            <th className="text-xs font-medium text-gray-600 text-right px-3 py-2 w-[60px]">AST</th>
            <th className="text-xs font-medium text-gray-600 text-right px-3 py-2 w-[60px]">득점</th>
          </tr>
        </thead>
        <tbody>
          {players.map((player, index) => (
            <tr key={index} className="border-b border-gray-100 hover:bg-gray-50">
              <td className="py-2 px-3">
                <div className="flex items-center gap-2">
                  <span className="text-gray-400 text-sm w-6">{player.number}</span>
                  <span className="text-sm text-gray-900">{player.name}</span>
                  <span className="text-xs text-gray-400">{player.position}</span>
                </div>
              </td>
              <td className="text-right text-sm tabular-nums px-3">{player.minutes}</td>
              <td className="text-right text-sm tabular-nums px-3">{player.rebounds}</td>
              <td className="text-right text-sm tabular-nums px-3">{player.assists}</td>
              <td className="text-right text-sm font-medium tabular-nums px-3">{player.points}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// Game records table
function GameRecordsTable({
  records,
  homeTeam,
  awayTeam
}: {
  records: GameData['gameRecords'];
  homeTeam: string;
  awayTeam: string;
}) {
  if (!records) return null;

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="bg-gray-50 border-b border-gray-200">
            <th className="text-xs font-medium text-gray-600 text-center px-3 py-2 w-[120px]">{homeTeam}</th>
            <th className="text-xs font-medium text-gray-600 text-center px-3 py-2">항목</th>
            <th className="text-xs font-medium text-gray-600 text-center px-3 py-2 w-[120px]">{awayTeam}</th>
          </tr>
        </thead>
        <tbody>
          {records.map((record, index) => (
            <tr key={index} className="border-b border-gray-100 hover:bg-gray-50">
              <td className="text-center text-sm tabular-nums px-3 py-2">{record.home}</td>
              <td className="text-center text-sm text-gray-600 px-3 py-2">{record.label}</td>
              <td className="text-center text-sm tabular-nums px-3 py-2">{record.away}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default GameResultViewer;
