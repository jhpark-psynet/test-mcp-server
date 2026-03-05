import type { BaseballTeamInfo, BaseballHeadToHead, RecentGameResult } from '../types';

interface TeamComparisonProps {
  homeTeam: BaseballTeamInfo;
  awayTeam: BaseballTeamInfo;
  headToHead?: BaseballHeadToHead;
}

export function TeamComparison({ homeTeam, awayTeam, headToHead }: TeamComparisonProps) {
  const hasRecentGames = !!(homeTeam.recentGames?.length || awayTeam.recentGames?.length);
  const hasHeadToHead = !!headToHead && headToHead.totalGames > 0;

  if (!hasRecentGames && !hasHeadToHead) return null;

  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
      <div className="px-3 py-2 bg-gray-50 border-b border-gray-200">
        <h3 className="text-sm font-semibold text-gray-800">팀 비교</h3>
      </div>

      {/* 팀 헤더 */}
      <div className="px-3 py-2 border-b border-gray-100">
        <div className="flex items-center justify-between">
          <TeamLogoName team={homeTeam} />
          <span className="text-gray-400 text-xs">vs</span>
          <TeamLogoName team={awayTeam} reversed />
        </div>
      </div>

      {/* 최근 5경기 */}
      {hasRecentGames && (
        <div className="px-4 py-3 border-b border-gray-100">
          <div className="text-xs font-medium text-gray-500 mb-2 text-center">최근 5경기</div>
          <div className="flex items-center justify-between">
            <RecentGamesDisplay games={homeTeam.recentGames} />
            <RecentGamesDisplay games={awayTeam.recentGames} reversed />
          </div>
        </div>
      )}

      {/* 맞대결 */}
      {hasHeadToHead && (
        <div className="px-4 py-3">
          <div className="text-xs font-medium text-gray-500 mb-2 text-center">시즌 상대전적</div>
          <div className="flex items-center justify-center gap-6 text-sm">
            <div className="text-center">
              <div className="font-bold text-blue-600 text-xl">{headToHead.homeWins}</div>
              <div className="text-xs text-gray-500">{homeTeam.shortName}</div>
            </div>
            {headToHead.draws > 0 && (
              <div className="text-center">
                <div className="font-bold text-gray-500 text-xl">{headToHead.draws}</div>
                <div className="text-xs text-gray-500">무</div>
              </div>
            )}
            <div className="text-center">
              <div className="font-bold text-blue-600 text-xl">{headToHead.awayWins}</div>
              <div className="text-xs text-gray-500">{awayTeam.shortName}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function TeamLogoName({ team, reversed }: { team: BaseballTeamInfo; reversed?: boolean }) {
  const logo = team.logo ? (
    <img src={team.logo} alt={team.name} className="w-8 h-8 object-contain" />
  ) : (
    <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center text-[10px] font-semibold text-gray-600">
      {team.shortName.slice(0, 2)}
    </div>
  );

  return (
    <div className={`flex items-center gap-2 ${reversed ? 'flex-row-reverse' : ''}`}>
      {logo}
      <span className="font-medium text-gray-800 text-sm">{team.shortName}</span>
    </div>
  );
}

function RecentGamesDisplay({
  games,
  reversed,
}: {
  games?: RecentGameResult[];
  reversed?: boolean;
}) {
  if (!games || games.length === 0) return null;

  return (
    <div className={`flex gap-1 ${reversed ? 'flex-row-reverse' : ''}`}>
      {games.slice(0, 5).map((result, idx) => (
        <div
          key={idx}
          className={`w-6 h-6 flex items-center justify-center text-[11px] font-bold rounded ${
            result === 'W'
              ? 'bg-blue-600 text-white'
              : result === 'D'
              ? 'bg-gray-400 text-white'
              : 'bg-gray-200 text-gray-600'
          }`}
        >
          {result}
        </div>
      ))}
    </div>
  );
}

export default TeamComparison;
