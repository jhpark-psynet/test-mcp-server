import type { BaseballGameRecord, BaseballTeamInfo } from '../types';

interface GameRecordsProps {
  homeTeam: BaseballTeamInfo;
  awayTeam: BaseballTeamInfo;
  gameRecords: BaseballGameRecord[];
}

export function GameRecords({ homeTeam, awayTeam, gameRecords }: GameRecordsProps) {
  if (!gameRecords || gameRecords.length === 0) return null;

  return (
    <div className="bg-white border border-gray-200 rounded-lg">
      <div className="px-3 py-2 border-b border-gray-100">
        <h3 className="text-sm font-semibold text-gray-800">팀 스탯</h3>
      </div>
      <div className="p-2">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-xs font-bold">
              <th className="text-center py-1 w-16 text-gray-800">{homeTeam.shortName}</th>
              <th className="text-center py-1 text-gray-500">항목</th>
              <th className="text-center py-1 w-16 text-gray-800">{awayTeam.shortName}</th>
            </tr>
          </thead>
          <tbody>
            {gameRecords.map((record, idx) => {
              const homeRaw = typeof record.home === 'number'
                ? record.home
                : parseFloat(String(record.home)) || 0;
              const awayRaw = typeof record.away === 'number'
                ? record.away
                : parseFloat(String(record.away)) || 0;

              // 낮을수록 유리한 항목
              const isLowerBetter = ['실책', '팀ERA'].includes(record.label);
              const homeWins = isLowerBetter ? homeRaw < awayRaw : homeRaw > awayRaw;
              const awayWins = isLowerBetter ? awayRaw < homeRaw : awayRaw > homeRaw;

              return (
                <tr key={idx} className="border-t border-gray-100">
                  <td
                    className="text-center py-1 tabular-nums"
                    style={{ color: homeWins ? '#2563eb' : '#374151', fontWeight: homeWins ? 700 : 400 }}
                  >
                    {record.home}
                  </td>
                  <td className="text-center py-1 text-xs text-gray-500">{record.label}</td>
                  <td
                    className="text-center py-1 tabular-nums"
                    style={{ color: awayWins ? '#2563eb' : '#374151', fontWeight: awayWins ? 700 : 400 }}
                  >
                    {record.away}
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

export default GameRecords;
