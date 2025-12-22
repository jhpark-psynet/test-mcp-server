import type { BasketballGameRecord, BasketballTeamInfo } from '../types';

interface GameRecordsProps {
  homeTeam: BasketballTeamInfo;
  awayTeam: BasketballTeamInfo;
  gameRecords: BasketballGameRecord[];
}

export function GameRecords({ homeTeam, awayTeam, gameRecords }: GameRecordsProps) {
  if (!gameRecords || gameRecords.length === 0) return null;

  return (
    <div className="bg-white border border-gray-200 rounded-lg">
      <div className="px-3 py-2 border-b border-gray-100">
        <h3 className="text-sm font-semibold text-gray-800">경기 기록</h3>
      </div>

      <div className="p-2">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-xs font-bold" style={{ color: '#1f2937' }}>
              <th className="text-center py-1 w-16">{homeTeam.shortName}</th>
              <th className="text-center py-1" style={{ color: '#374151' }}>항목</th>
              <th className="text-center py-1 w-16">{awayTeam.shortName}</th>
            </tr>
          </thead>
          <tbody>
            {gameRecords.map((record, idx) => {
              const homeValue = typeof record.home === 'number' ? record.home : parseFloat(record.home) || 0;
              const awayValue = typeof record.away === 'number' ? record.away : parseFloat(record.away) || 0;

              const isLowerBetter = record.label === '턴오버' || record.label === '파울' || record.label === 'Turnovers' || record.label === 'Fouls';
              const homeWins = isLowerBetter ? homeValue < awayValue : homeValue > awayValue;
              const awayWins = isLowerBetter ? awayValue < homeValue : awayValue > homeValue;

              return (
                <tr key={idx} className="border-t border-gray-100">
                  <td
                    className="text-center py-1 tabular-nums"
                    style={{ color: homeWins ? '#2563eb' : '#374151', fontWeight: homeWins ? 700 : 400 }}
                  >
                    {record.home}
                  </td>
                  <td className="text-center py-1 text-xs" style={{ color: '#4b5563' }}>{record.label}</td>
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
