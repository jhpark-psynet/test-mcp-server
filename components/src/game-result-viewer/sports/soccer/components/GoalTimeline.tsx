import type { GoalEvent, SoccerTeamInfo } from '../types';

interface GoalTimelineProps {
  goals: GoalEvent[];
  homeTeam: SoccerTeamInfo;
  awayTeam: SoccerTeamInfo;
}

export function GoalTimeline({ goals, homeTeam, awayTeam }: GoalTimelineProps) {
  if (!goals || goals.length === 0) return null;

  const homeColor = homeTeam.primaryColor || '#3b82f6';
  const awayColor = awayTeam.primaryColor || '#ef4444';

  // 시간순 정렬
  const sortedGoals = [...goals].sort((a, b) => {
    const aTime = a.minute + (a.addedTime || 0) / 100;
    const bTime = b.minute + (b.addedTime || 0) / 100;
    return aTime - bTime;
  });

  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-sm">
      <div className="px-3 py-2 border-b border-gray-100">
        <h3 className="text-sm font-medium" style={{ color: '#1f2937' }}>골 타임라인</h3>
      </div>

      <div className="p-3 space-y-2">
        {sortedGoals.map((goal, idx) => {
          const isHome = goal.team === 'home';
          const teamColor = isHome ? homeColor : awayColor;

          return (
            <div
              key={idx}
              className={`flex items-center gap-3 p-2 rounded-lg ${
                isHome ? 'flex-row' : 'flex-row-reverse'
              }`}
              style={{
                background: `linear-gradient(${isHome ? 'to right' : 'to left'}, ${teamColor}10, transparent)`,
              }}
            >
              <span
                className="text-xs font-bold px-2 py-1 rounded text-white"
                style={{ background: teamColor }}
              >
                {goal.minute}{goal.addedTime ? `+${goal.addedTime}` : ''}'
              </span>
              <div className={`flex flex-col ${isHome ? '' : 'items-end'}`}>
                <span className="text-sm font-medium" style={{ color: '#1f2937' }}>
                  {goal.scorer}
                  {goal.isPenalty && <span className="ml-1 text-xs" style={{ color: '#4b5563' }}>(PK)</span>}
                  {goal.isOwnGoal && <span className="ml-1 text-xs" style={{ color: '#dc2626' }}>(자책골)</span>}
                </span>
                {goal.assist && (
                  <span className="text-xs" style={{ color: '#6b7280' }}>
                    어시스트: {goal.assist}
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default GoalTimeline;
