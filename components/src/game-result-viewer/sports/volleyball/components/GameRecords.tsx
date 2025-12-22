import type { VolleyballGameRecord, VolleyballTeamInfo } from '../types';

interface GameRecordsProps {
  homeTeam: VolleyballTeamInfo;
  awayTeam: VolleyballTeamInfo;
  gameRecords: VolleyballGameRecord[];
}

export function GameRecords({ homeTeam, awayTeam, gameRecords }: GameRecordsProps) {
  if (!gameRecords || gameRecords.length === 0) return null;

  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-sm">
      <div className="px-3 py-2 border-b border-gray-100">
        <h3 className="text-sm font-medium" style={{ color: '#1f2937' }}>경기 기록</h3>
      </div>

      <div className="p-2">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-xs" style={{ color: '#4b5563' }}>
              <th className="text-center py-1 w-20" style={{ color: homeTeam.primaryColor }}>
                {homeTeam.shortName}
              </th>
              <th className="text-center py-1">항목</th>
              <th className="text-center py-1 w-20" style={{ color: awayTeam.primaryColor }}>
                {awayTeam.shortName}
              </th>
            </tr>
          </thead>
          <tbody style={{ color: '#1f2937' }}>
            {gameRecords.map((record, idx) => {
              const homeValue = typeof record.home === 'number' ? record.home : parseFloat(String(record.home)) || 0;
              const awayValue = typeof record.away === 'number' ? record.away : parseFloat(String(record.away)) || 0;

              const isLowerBetter = record.label === '서브 실책' || record.label === '실책';
              const homeWins = isLowerBetter ? homeValue < awayValue : homeValue > awayValue;
              const awayWins = isLowerBetter ? awayValue < homeValue : awayValue > homeValue;

              return (
                <tr key={idx} className="border-t border-gray-100">
                  <td
                    className="text-center py-1.5 tabular-nums"
                    style={{ color: homeWins ? '#2563eb' : '#1f2937', fontWeight: homeWins ? 700 : 400 }}
                  >
                    {record.home}
                  </td>
                  <td className="text-center py-1.5 text-xs" style={{ color: '#4b5563' }}>{record.label}</td>
                  <td
                    className="text-center py-1.5 tabular-nums"
                    style={{ color: awayWins ? '#2563eb' : '#1f2937', fontWeight: awayWins ? 700 : 400 }}
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
