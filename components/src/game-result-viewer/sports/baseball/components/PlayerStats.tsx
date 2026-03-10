import { useState } from 'react';
import type { BaseballTeamInfo, BaseballBatterStats, BaseballPitcherStats } from '../types';

interface PlayerStatsProps {
  homeTeam: BaseballTeamInfo;
  awayTeam: BaseballTeamInfo;
}

export function PlayerStats({ homeTeam, awayTeam }: PlayerStatsProps) {
  const [activeTeam, setActiveTeam] = useState<'home' | 'away'>('home');
  const [activeTab, setActiveTab] = useState<'batter' | 'pitcher'>('batter');
  const currentTeam = activeTeam === 'home' ? homeTeam : awayTeam;

  const hasData =
    homeTeam.batters.length > 0 || homeTeam.pitchers.length > 0 ||
    awayTeam.batters.length > 0 || awayTeam.pitchers.length > 0;

  if (!hasData) return null;

  return (
    <div className="bg-white border border-gray-200 rounded-lg">
      {/* 팀 탭 */}
      <div className="flex border-b border-gray-200">
        <button
          onClick={() => setActiveTeam('home')}
          className={`flex-1 px-3 py-2 text-sm font-semibold border-b-2 ${
            activeTeam === 'home'
              ? 'border-red-600 text-red-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          {homeTeam.shortName}
        </button>
        <button
          onClick={() => setActiveTeam('away')}
          className={`flex-1 px-3 py-2 text-sm font-semibold border-b-2 ${
            activeTeam === 'away'
              ? 'border-red-600 text-red-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          {awayTeam.shortName}
        </button>
      </div>

      {/* 타자/투수 탭 */}
      <div className="flex border-b border-gray-100 bg-gray-50">
        <button
          onClick={() => setActiveTab('batter')}
          className={`flex-1 px-3 py-1.5 text-xs font-medium ${
            activeTab === 'batter' ? 'text-red-600 font-semibold' : 'text-gray-500'
          }`}
        >
          타자
        </button>
        <button
          onClick={() => setActiveTab('pitcher')}
          className={`flex-1 px-3 py-1.5 text-xs font-medium ${
            activeTab === 'pitcher' ? 'text-red-600 font-semibold' : 'text-gray-500'
          }`}
        >
          투수
        </button>
      </div>

      {/* 스탯 테이블 */}
      <div className="p-2 overflow-x-auto">
        {activeTab === 'batter' ? (
          <BatterTable batters={currentTeam.batters} />
        ) : (
          <PitcherTable pitchers={currentTeam.pitchers} />
        )}
      </div>
    </div>
  );
}

function BatterTable({ batters }: { batters: BaseballBatterStats[] }) {
  if (batters.length === 0) {
    return <div className="text-center text-gray-400 text-sm py-4">데이터 없음</div>;
  }

  const showOps = batters.some(b => b.ops !== undefined && b.ops !== '-');

  return (
    <table className="w-full text-xs">
      <thead>
        <tr className="border-b border-gray-200">
          <th className="text-left px-1 py-1 text-gray-600 font-semibold">타자</th>
          <th className="text-center px-1 py-1 text-gray-600 font-semibold w-6 whitespace-nowrap">타석</th>
          <th className="text-center px-1 py-1 text-gray-600 font-semibold w-6 whitespace-nowrap">안타</th>
          <th className="text-center px-1 py-1 text-gray-600 font-semibold w-6 whitespace-nowrap">홈런</th>
          <th className="text-center px-1 py-1 text-gray-600 font-semibold w-6 whitespace-nowrap">타점</th>
          <th className="text-center px-1 py-1 text-gray-600 font-semibold w-6 whitespace-nowrap">볼</th>
          <th className="text-center px-1 py-1 text-gray-600 font-semibold w-6 whitespace-nowrap">삼진</th>
          <th className="text-center px-1 py-1 text-gray-600 font-semibold w-10 whitespace-nowrap">타율</th>
          <th className="text-center px-1 py-1 text-gray-600 font-semibold w-10 whitespace-nowrap">출루</th>
          {showOps && <th className="text-center px-1 py-1 text-gray-600 font-semibold w-10 whitespace-nowrap">OPS</th>}
        </tr>
      </thead>
      <tbody>
        {batters.map((batter, idx) => (
          <tr key={idx} className="border-b border-gray-100 hover:bg-gray-50">
            <td className="py-1 px-1">
              <div className="flex items-center gap-1">
                <span className="text-gray-400 w-3 text-right">{batter.batOrder}</span>
                <span className="text-gray-800">{batter.name}</span>
                <span className="text-gray-400">{batter.position}</span>
              </div>
            </td>
            <td className="text-center tabular-nums px-1 text-gray-700">{batter.atBats}</td>
            <td className={`text-center tabular-nums px-1 font-medium ${batter.hits > 0 ? 'text-blue-700' : 'text-gray-700'}`}>
              {batter.hits}
            </td>
            <td className={`text-center tabular-nums px-1 font-medium ${batter.homeRuns > 0 ? 'text-red-600' : 'text-gray-700'}`}>
              {batter.homeRuns}
            </td>
            <td className="text-center tabular-nums px-1 text-gray-700">{batter.rbi}</td>
            <td className="text-center tabular-nums px-1 text-gray-700">{batter.walks}</td>
            <td className="text-center tabular-nums px-1 text-gray-700">{batter.strikeouts}</td>
            <td className="text-center tabular-nums px-1 text-gray-600">{batter.avg}</td>
            <td className="text-center tabular-nums px-1 text-gray-600">{batter.obp}</td>
            {showOps && <td className="text-center tabular-nums px-1 text-gray-600">{batter.ops}</td>}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function PitcherTable({ pitchers }: { pitchers: BaseballPitcherStats[] }) {
  if (pitchers.length === 0) {
    return <div className="text-center text-gray-400 text-sm py-4">데이터 없음</div>;
  }

  const getResultColor = (result: string) => {
    if (result === '승') return 'text-blue-600 font-bold';
    if (result === '패') return 'text-red-600 font-bold';
    if (result === '세') return 'text-green-600 font-bold';
    return 'text-gray-600';
  };

  const showEra = pitchers.some(p => p.era !== undefined && p.era !== '-');
  const showWhip = pitchers.some(p => p.whip !== undefined && p.whip !== '-');

  return (
    <table className="w-full text-xs">
      <thead>
        <tr className="border-b border-gray-200">
          <th className="text-left px-1 py-1 text-gray-600 font-semibold">투수</th>
          <th className="text-center px-1 py-1 text-gray-600 font-semibold w-8 whitespace-nowrap">이닝</th>
          <th className="text-center px-1 py-1 text-gray-600 font-semibold w-6 whitespace-nowrap">구수</th>
          <th className="text-center px-1 py-1 text-gray-600 font-semibold w-6 whitespace-nowrap">피안</th>
          <th className="text-center px-1 py-1 text-gray-600 font-semibold w-6 whitespace-nowrap">탈삼</th>
          <th className="text-center px-1 py-1 text-gray-600 font-semibold w-6 whitespace-nowrap">실점</th>
          <th className="text-center px-1 py-1 text-gray-600 font-semibold w-6 whitespace-nowrap">자책</th>
          {showEra && <th className="text-center px-1 py-1 text-gray-600 font-semibold w-10 whitespace-nowrap">ERA</th>}
          {showWhip && <th className="text-center px-1 py-1 text-gray-600 font-semibold w-10 whitespace-nowrap">WHIP</th>}
        </tr>
      </thead>
      <tbody>
        {pitchers.map((pitcher, idx) => (
          <tr key={idx} className="border-b border-gray-100 hover:bg-gray-50">
            <td className="py-1 px-1">
              <div className="flex items-center gap-1">
                {pitcher.isStarter && (
                  <span className="text-xs bg-gray-100 text-gray-500 px-1 rounded">선발</span>
                )}
                <span className="text-gray-800">{pitcher.name}</span>
                {pitcher.result && (
                  <span className={`text-xs ${getResultColor(pitcher.result)}`}>
                    ({pitcher.result})
                  </span>
                )}
              </div>
            </td>
            <td className="text-center tabular-nums px-1 text-gray-700">{pitcher.innings}</td>
            <td className="text-center tabular-nums px-1 text-gray-700">{pitcher.pitchCount}</td>
            <td className="text-center tabular-nums px-1 text-gray-700">{pitcher.hits}</td>
            <td className="text-center tabular-nums px-1 text-gray-700">{pitcher.strikeouts}</td>
            <td className="text-center tabular-nums px-1 text-gray-700">{pitcher.runs}</td>
            <td className="text-center tabular-nums px-1 text-gray-700">{pitcher.earnedRuns}</td>
            {showEra && <td className="text-center tabular-nums px-1 text-gray-600">{pitcher.era}</td>}
            {showWhip && <td className="text-center tabular-nums px-1 text-gray-600">{pitcher.whip}</td>}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default PlayerStats;
